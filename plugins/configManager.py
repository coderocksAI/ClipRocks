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
import json

class ConfigManager:
    """
    Manages configuration settings by reading from and writing to a JSON file (configCache used by ClipRocks).
    
    The class allows for initializing the configuration based on a root directory and an optional plugin name.
    It provides methods to read, write, and update configuration options.
    """
    def __init__(self, rootConfig, dataConfig=None, pluginName=None):
        """
        Initializes the ConfigManager object.
        """

        # root folder where config can be read/write
        self.rootConfig = rootConfig
        self.dataConfig = dataConfig

        # stored when config.json exist or just after created.
        self.configCache = None

        # default config
        self.configFileName = "config.conf"
        self.pluginsNameFolder = "plugins"

        # pluginName
        self.pluginName = pluginName
        if (self.pluginName):
            self.pluginName = f"{pluginName}Plugin"

        # root/plugin folder & config file 
        self._set_plugin_folder_and_json()

    def initialize_default_config(self, dataConfig):
        """
        Initializes the default configuration by creating a ConfigManager object with the 
        absolute directory script.

        If the configuration file does not exist, it calculates derived paths and writes 
        the configuration to the file. Otherwise, it reads the configuration from the file
        using the read_config method.
        """
        if not self.is_config_file_exists():
            self.configCache = self.write_config(dataConfig)
        else:
            self.configCache = self.read_config()


    def _set_plugin_folder_and_json(self):
        """
        Sets the plugin-specific folder and config file path based on the plugin name.
        
        If a plugin name is provided, it sets up the plugin-specific folder and config file.
        Otherwise, it uses the root configuration directory.
        """
        if self.pluginName:
            self.PluginFolder = os.path.join(self.rootConfig, self.pluginsNameFolder, self.pluginName.lower())
            self.configPath = os.path.join(self.PluginFolder, self.configFileName)
        else:
            self.PluginFolder = None
            self.configPath = os.path.join(self.rootConfig, self.configFileName)

    def is_config_file_exists(self):
        """
        Checks if the configuration file exists.
        """
        #print(self.configPath)
        return os.path.exists(self.configPath)

    def read_config(self, use_cache=True) -> dict:
        """
        Retrieves the configuration with intelligent cache management.
        
        If caching is enabled and a valid cached copy exists, it returns the cached copy.
        Otherwise, it reads the configuration from the file and updates the cache.
        """
        if use_cache and self.configCache is not None:
            return self.configCache
        elif not self.is_config_file_exists():
            return {}
        with open(self.configPath, 'r', encoding="utf-8") as file:
            raw_json = file.read()
            raw_json = raw_json.replace("\\", "\\\\")  # We reset the double backslashes
            self.configCache = json.loads(raw_json, strict=False)  # Disable strict verification
            return self.configCache

    def write_config(self, config: dict):
        """
        Write a configuration JSON file with single backslashes.
        """
        if self.is_config_file_exists():
            raise KeyError("Write_config is not allowed to overwrite an existing configuration.")

        # Convertir en JSON sans échappement
        json_string = json.dumps(config, indent=4)  # Génère le JSON normalement
        json_string = json_string.replace("\\\\", "\\")  # Remplace les \\ par \

        # Écrire le JSON en mode texte brut
        with open(self.configPath, "w", encoding="utf-8") as f:
            f.write(json_string)

        return config

    def read_option(self, key, use_cache=True):
        """
        Retrieves a value of a configuration from cache if use_cache=True 
        and cache exist.
        """
        if use_cache and self.configCache is not None:
            return self.configCache[key]
        elif not self.is_config_file_exists():
            raise FileNotFoundError("The config file does not exist.")

        with open(self.configPath, 'r') as file:
            config = json.load(file)
            if key in config:
                return config[key]
            else:
                raise KeyError(f"The option '{key}' does not exist in the config file.")

    def write_option(self, option_name, value):
        """
        Writes or updates a specific configuration option in the file.
        """
        if not self.is_config_file_exists():
            with open(self.configPath, 'w') as file:
                json.dump({}, file)

        with open(self.configPath, 'r+') as file:
            config = json.load(file)
            config[option_name] = value
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()

    def create_config_file(self):
        """
        Creates an empty configuration file if it does not exist.
        """
        if not os.path.exists(self.configPath):
            with open(self.configPath, 'w') as file:
                json.dump({}, file)

    def get_root_config(self):
        """
        Retrieves the root configuration directory.
        """
        return self.rootConfig

    def getRootPath(self):
        """
        get root folder where config can be read/write
        """
        return self.rootConfig
        
    def get_plugin_name(self):
        """
        Retrieves the plugin name if specified.
        """
        return self.pluginName

    def get_plugin_folder(self):
        """
        Retrieves the absolute path to the plugin-specific folder.
        """
        return self.PluginFolder

    def get_config_path(self):
        """
        Retrieves the absolute path to the configuration file.
        """
        return self.configPath