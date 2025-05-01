#!/usr/bin/env python3

"""
    ClipRocks is a scripting tool for DaVinci Resolve that enables instant copying and pasting
    of content into the timeline, with optional AI-powered features such as background removal
    and image upscaling.

    Copyright: (C) 2025, coderocksai https://github.com/coderocksAI/ClipRocks
    youtube channel : https://www.youtube.com/@CodeRocks
    website : coderocks.fr 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from plugins.virtualEnvHelper import VirtualEnvHelper
from plugins.configManager import ConfigManager
from guiManager import GUIManager
from clipElement import ClipElement
from davinciAPI import DaVinciAPI
import inspect

class ClipRocks:
    def __init__(self, resolve):
        """
        Initializes the ClipRocks engine as the main entry point of the system every time DaVinci Resolve 
        is launched (keyboard shortcut). It coordinates the context between different types of clipboard 
        elements (see clipElement) and the plugin initialization loop (see HandlePlugins and plugin_instance.
        display_button). Plugin execution occurs when an available button is clicked (see on_button_click).

        Note: Consider implementing a conditional initialization method for plugins to check their compatibility
         with the clipboard without instantiating them each time. (like a static Plugin.is_able(code))
        """

        # Retrieves the absolute path of the current script file.
        abs_path_script = self._getCurrentPathScript()

        # Retrieves the absolute directory containing the current script file.
        abs_dir_script = self._getCurrentDirScript(abs_path_script)


        """──────────────────────────────────────────────────────────────────────────────────
        Configuration Initialization (ConfigManager)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        self.default_config = {

            # for logic -> ?blackmagic?/rootName/PluginCode (light)
            # for storage -> ?base?/rootName/[venv,assets,cache] (can be big)
            "rootName": "ClipRocks",  

            # Virtual folder in DaVinci GUI.
            "binName": "__ClipRocks__", 

            # for storage
            "base": os.path.expanduser("~\\Documents"),

            # Absolute path of this script (for now, no used ? maybe useless)
            "abs_path_script" : abs_path_script,

            # Absolute path dir of this script 
            # To read config.json in this folder and each plugins folders
            "abs_dir_script" : abs_dir_script,  

        }

        # reads or init and write config ([default_config + derivated_config])
        # note : maybe, can more simple if self.configCache direcly used ? 
        self.config = ConfigManager(self.default_config["abs_dir_script"])
        self.config.initialize_default_config({**self.default_config, **self._calculate_derived_paths()})

        """──────────────────────────────────────────────────────────────────────────────────
        VirtuelEnv Initialization (VirtualEnvHelper)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        self.venvPath = self.config.read_option("venv")
        self.venv = self._initVirtualEnv(self.venvPath)


        """──────────────────────────────────────────────────────────────────────────────────
        Clipboard (ClipElement)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        self.clipboard_element = ClipElement()
        

        """──────────────────────────────────────────────────────────────────────────────────
        Davinci API (DaVinciAPI)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        # init Davinci API with default virtual folder and native API resolve from software
        self.davinciAPI = DaVinciAPI(resolve, self.config.read_option("binName"))

        # Plugin button registry
        self.button_registry = {}

        # where to work and save + auto add folder (!!! Note : need self.davinciAPI instanciated)
        self.asset_save_path = self._construct_folder_path(self.config.read_option("assets"))
        self.cache_save_path = self._construct_folder_path(self.config.read_option("cache"))


        """──────────────────────────────────────────────────────────────────────────────────
        GUI list buttons (GUIManager)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        self.gui_manager = GUIManager(self)


    def _calculate_derived_paths(self):
        """
        Calculates derived paths based on the base directory and root name specified 
        in the default configuration.
        """
        base_root = os.path.join(self.default_config["base"], self.default_config["rootName"])
        return {

            # for storage medias files : ~base/baseRoot/
            "baseRoot": base_root,

            # ~base/baseRoot/venv
            "venv": os.path.join(base_root, "venv"),

            # ~base/baseRoot/assets
            "assets": os.path.join(base_root, "assets"),

            # ~base/baseRoot/cache
            "cache": os.path.join(base_root, "cache"),
            
            # ~base/baseRoot/cache
            "plugins": os.path.join(base_root, "plugins")
        }

    def _getCurrentPathScript(self):
        """
        get absolute path of this main script to know where our script is running.
        
        Note: The inspect method is not the most optimized, but it is the only functional
        one in an execution context controlled by davinci resolve as a script engine.
        """
        return inspect.currentframe().f_code.co_filename 

    def _getCurrentDirScript(self, abs_path_script):
        """
        Returns the current script's directory path from _getCurrentPathScript.
        """
        return os.path.dirname(os.path.abspath(abs_path_script))

    def _initVirtualEnv(self, venvPath):
        """
        Initializes the virtual environment located at `venvPath` and activates it for the current Python process
        by editing env variables (sys.path, VIRTUAL_ENV, et PATH).
        """
        try:
            virtualEnv = VirtualEnvHelper(venvPath)
            virtualEnv.activate_for_current_process()
            return virtualEnv
        except Exception as e:
            raise RuntimeError(f"Failed to initialize virtual environment at {venvPath}. Error: {e}")


    def _construct_folder_path(self, path):
        """
        Constructs folder path based on the configuration and the current project name.
        """
        os.makedirs(path, exist_ok=True)

        # Check Name project from davinci Resolve
        project_name = self.davinciAPI.getCurrentProjectName()
        if not project_name or project_name.strip() == "" or project_name == "Untitled Project":
            print("Alert : Save your DaVinci Resolve project to create a dedicated assets path.")
            return None

        # make specific folder from project name
        project_path = os.path.join(path, project_name)
        os.makedirs(project_path, exist_ok=True)

        return project_path

    def _load_plugins(self):
        """
        Dynamically loads all plugins after virtualenv activation.
        Each plugin must be in a subdirectory with a 'main.py' file.
        """
        """
        This module automatically discovers and imports all Python modules found in 
        subdirectories within the 'plugins' directory. Each subdirectory should contain
        a file named 'main.py'. The name of the imported module is constructed as 
        'plugins.{subdirectory_name}.main'.

        The script iterates over each item in the 'plugins' directory. If an item is 
        a directory, it checks for the presence of a 'main.py' file within that directory.
        If found, it constructs the module name and attempts to import it using 
        importlib.import_module(). Any ImportError encountered during this process is caught
        and printed with an error message.

        This approach simplifies the process of managing plugins by automatically importing 
        them without manual intervention.
        """
        plugin_dir = os.path.join(self.config.read_option("abs_dir_script"), "plugins")
        for plugin_name in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, plugin_name)
            if os.path.isdir(plugin_path):
                main_file = os.path.join(plugin_path, "main.py")
                if os.path.isfile(main_file):
                    try:
                        module_name = f"plugins.{plugin_name}.main"
                        importlib.import_module(module_name)
                    except ImportError as e:
                        print(f"Plugin '{plugin_name}' failed to import: {e}")


    def register_button(self, button_name, plugin_instance):        
        """
        Registers a button with its associated plugin instance and GUI. Once registered, the button 
        can be clicked, and when clicked, it will trigger the associated plugin's functionality.
        """
        self.button_registry[button_name] = plugin_instance
        self.gui_manager.add_button(button_name, plugin_instance)


    def on_button_click(self, button_name):
        """
        Handles the button click by executing the associated plugin. This method ensures that when a
        button is clicked, the corresponding plugin's functionality and behavior are executed

        Checks associated plugin instance for the given button name in the `button_registry`.
        If exists, it retrieves the media object by calling the `execute` method of the plugin.
        stop GUI
        """
        if button_name in self.button_registry:
            plugin_instance = self.button_registry[button_name]

            if (plugin_instance.is_install()):
                media = plugin_instance.execute(self.clipboard_element)

                # Étape 2 : Sauvegarder
                asset_SAVED_path = media.save(self.asset_save_path)

                # Étape 3 : Ajouter au bin
                binFolder = self.davinciAPI.get_or_create_bin()
                self.davinciAPI.add_to_bin(binFolder, asset_SAVED_path)
            
                # Étape 4 : Ajouter à la timeline
                clip_name = media.get_filename()
                currentFolder = self.davinciAPI.getCurrentFolder()
                clips = currentFolder.GetClipList()
                clip = self.davinciAPI.get_item_by_name(clips, clip_name)

                listClips = self.davinciAPI.add_to_timeline([{
                    "mediaPoolItem": clip,
                }])
            else:
                self.gui_manager.disable_close_focus_out()
                plugin_instance.install()
                self.gui_manager.enable_close_focus_out()
            
            self.gui_manager.exit()
            sys.exit(0)
        else:
            print(f"No plugin associated with button: {button_name}")
            
    def HandlePlugins(self):
        """
        Activates plugins based on clipboard conditions and displays buttons. This method ensures 
        that only plugins meeting specific clipboard conditions are activated and their buttons 
        are displayed in the GUI for interaction.

        1. Retrieves the format IDs from the clipboard element.
        2. Iterates through each plugin registered in `plugin_registry`and instanciate each plugin
        3. Checks plugin compatibility with clipboard format IDs, display if ok. 
        4. after loop, run GUI. 
        """
        format_ids = self.clipboard_element.get_format_ids()

        # activate main venv
        self.venv.activate_for_current_process()

        # load plugin registry
        from plugins.pluginBase import plugin_registry

        # dynamic import plugins after venv
        self._load_plugins()

        for plugin_name, plugin_class in plugin_registry.items():
            plugin_instance = None

            plugin_instance = plugin_class(
                configRoot = self.config,
                venv = self.venv, 
                clipboard_element = self.clipboard_element, 
                cache_save_path = self.cache_save_path
            )

            if plugin_instance.check_condition(format_ids):
                button = plugin_instance.display_button()
                self.register_button(button, plugin_instance)

        # Run the GUI after all buttons are registered
        self.gui_manager.run()
                
ClipRocks = ClipRocks(resolve)
ClipRocks.HandlePlugins()