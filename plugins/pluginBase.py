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

from .virtualEnvHelper import VirtualEnvHelper
from .media import Media

import re

from .configManager import ConfigManager

# Global plugin registry
plugin_registry = {}

class PluginBase:
    def __init_subclass__(cls, **kwargs):
        """
        Automatically registers the plugin when it's defined.
        
        :param cls: The subclass being defined.
        :return: None
        """
        super().__init_subclass__(**kwargs)
        plugin_registry[cls.__name__] = cls

    #
    def __init__(self, *args, **kwargs):
        """
        Initializes the plugin with the clipboard element.
        """

        """──────────────────────────────────────────────────────────────────────────────────
        Configuration GLOBAL + PLUGIN (ConfigManager)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        
        self.pluginName = self.getClassName()
        self.configRoot = kwargs.get('configRoot')
        self.configPlugin = ConfigManager(
            self.configRoot.getRootPath(),
            pluginName = self.getClassName()
        )

        """──────────────────────────────────────────────────────────────────────────────────
        INIT PLUGIN CONFIGURATION BY CHILD PLUGIN OVERRIDE (ConfigManager)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        self.configuration = self.initConfiguration()
        if(self.configuration):
            self.configPlugin.initialize_default_config(
                self.configuration
            )

        """──────────────────────────────────────────────────────────────────────────────────
        Configuration virtual global environement (VirtualEnvHelper)
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        self.venv = kwargs.get('venv')
        self.venv.initVirtualEnv()


        """──────────────────────────────────────────────────────────────────────────────────
        Other Elements
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""
        self.clipboard_element = kwargs.get('clipboard_element')
        self.cache_save_path = self.configRoot.read_option("cache")


    def initConfiguration(self): 
        """
        This method is intended to be overridden by child classes. 
        It should return a dictionary containing the specific configuration for the plugin.
        """
        return None

    def getOption(self, optionName):
        """
        Returns the value of a configuration option (config.json).
        """
        return self.configRoot.read_option(optionName)

    def setOption(self, optionName, value):
        """
        Sets the value of a configuration option (config.json).
        """
        self.configRoot.write_option(optionName, value)
    
    def getClassName(self):
        """
        Returns the lowercase class name of the subclass.
        """
        return self.__class__.__name__.lower()

    def check_condition(self, format_ids):
        """
        Determines if the plugin should be activated. Must be implemented 
        by the plugin.
        """
        raise NotImplementedError

    def is_install(self):
        """
        check that the plugin is properly installed in the directory specified in its own 
        configuration file. This method should be overridden in child classes if needed.
        """
        return True


    def execute(self, media_info):
        """
        Executes the plugin logic. Must be implemented by the plugin.
        """
        raise NotImplementedError

    def extract_image_from_clipboard(self):
        """
        Checks if the clipboard contains an image and returns a Media object containing
        the image data.
        """
        raw_data = self.clipboard_element.get_raw_BITMAP()
        return Media(raw_content=raw_data, mime_type="image/png")


    def display_button(self):
        """
        Returns the name of the button to display in the UI. 
        Must be implemented by the plugin.
        """
        raise NotImplementedError

    def activate_shared_env(self):
        """
        Activates the shared virtual environment for the plugin if available.
        """
        if self.venv:
            self.venv.activate_for_current_process()
            
    def use_virtual_env(self, venv_path):
        """
        Utility method to create a VirtualEnvHelper instance on demand.
        """
        return VirtualEnvHelper(venv_path)

    def is_url(self, text):
        """
        Checks if the provided text is a valid URL.
        """
        url_pattern = re.compile(r'https?://[^\s]+')
        return bool(url_pattern.match(text))

    def download_file_from_url(self, url):
        """
        Downloads the content of a URL and returns the binary content and MIME type.
        """
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            mime_type = response.headers.get('Content-Type', 'application/octet-stream')
            return response.content, mime_type
        except requests.RequestException as e:
            print(f"Error downloading file from URL: {e}")
            return None, None