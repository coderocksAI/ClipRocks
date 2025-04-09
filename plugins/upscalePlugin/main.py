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

from ..pluginBase import PluginBase
from ..media import Media
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import webbrowser

class Upscale(PluginBase):

    def is_install(self):
        binary = os.path.join(
            self.configPlugin.read_option('project_base'), 
            self.configPlugin.read_option('script_name'),
            )
        if not os.path.isfile(binary):
            return False
        return True

    def install(self):
         self.show_plugin_warning()


    def show_plugin_warning(self):
        def open_github():
            webbrowser.open_new("https://github.com/coderocksAI/ClipRocks")

        root = tk.Tk()
        root.withdraw()  # Cache the main window

        # Show a dialog box
        response = messagebox.askyesno(
            title="Plugin non installé",
            message=(
                "Le plugin 'upscayle' ne semble pas être installé sur votre dossier par défaut : \n\n"
                f"{self.configPlugin.read_option("project_base")}"
                "\n\n Souhaitez-vous ouvrir la page GitHub pour consulter les instructions d'installation ?"
            )
        )

        if response:
            open_github()

        # root.destroy()

    def initConfiguration(self):
        pluginsPath = os.path.join(self.configRoot.read_option('plugins'), self.pluginName)
        return {
            "project_base" : pluginsPath,
            "project_model" : os.path.join(pluginsPath, 'models'),
            "model_name" : "RealESRGAN_General_x4_v3",
            "script_name" : 'upscayl-bin.exe',
            "install": 'https://github.com/upscayl/upscayl-ncnn'
        }

    def check_condition(self, format_ids):
        """
        Activates the plugin if CF_BITMAP (2) is present in the clipboard formats.
        """
        return {2}.intersection(format_ids)

    def execute(self, clipboard_element):
        """
        Upscale an image using upscayl-bin.exe.
        """
        media = self.extract_image_from_clipboard()
        media.save(self.cache_save_path)  # Save the clipboard image in the cache

        # Define input and output paths
        input_path = media.get_path()
        file_root, file_extension = os.path.splitext(input_path)
        output_path = f"{file_root}-x2{file_extension}"

        # Path to upscayl-bin.exe
        project_base = self.configPlugin.read_option('project_base')
        script_name  = self.configPlugin.read_option('script_name')

        upscayl_bin = os.path.join(project_base, script_name)
        model_path =  os.path.join(project_base, script_name)

        model_name = self.configPlugin.read_option('model_name')

        # Run the subprocess
        process = subprocess.run(
            [
                upscayl_bin,
                "-i", input_path,
                "-o", output_path,
                "-n", model_name
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check for errors
        if process.returncode != 0:
            print(f"Upscale failed: {process.stderr}")
            raise RuntimeError("Upscale process failed.")

        # Update the media path to point to the upscaled image
        media.update_mimeType_path("image/png", output_path)

        return media  # Return the updated media object for ResolveAI to handle
    
    def display_button(self):
        return "UpScale"