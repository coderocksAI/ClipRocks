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
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import webbrowser


class RemBg(PluginBase):

    def show_plugin_warning(self):
        def open_github():
            webbrowser.open_new("https://github.com/coderocksAI/ClipRocks")

        root = tk.Tk()
        root.withdraw()  # Cache the main window

        # Show a dialog box
        response = messagebox.askyesno(
            title="Plugin non installé",
            message=(
                "Le plugin 'rembg' ne semble pas être installé sur votre dossier par défaut : \n\n"
                f"{self.configPlugin.read_option("project_base")}"
                "\n\n Souhaitez-vous ouvrir la page GitHub pour consulter les instructions d'installation ?"
            )
        )

        if response:
            open_github()

        # root.destroy()


    def install(self):
         self.show_plugin_warning()


    def initConfiguration(self):
        pluginsPath = os.path.join(self.configRoot.read_option('plugins'), self.pluginName)
        script_base = os.path.join(self.configRoot.read_option('abs_dir_script'), 'plugins', f"{self.pluginName}Plugin") 
        return {
            "base" : script_base,
            "project_base" : pluginsPath,
            "project_venv" : os.path.join(pluginsPath, 'venv'),
            "U2NET_HOME" : os.path.join(pluginsPath, 'u2net'),
            "script_name" : 'cliprembg.py',
            "install": 'rembg[cli] onnxruntime==1.20.1'
        }

    def is_install(self):
        venv_path = self.configPlugin.read_option('project_venv')
        rembg_lib = os.path.join(venv_path, "Lib", "site-packages", "rembg")
        rembg_exe = os.path.join(venv_path, "Scripts", "rembg.exe")

        if not os.path.exists(rembg_lib) or not os.path.exists(rembg_exe):
            return False
        return True
        

    def check_condition(self, format_ids):
        """
        Activates the plugin if CF_BITMAP (2) is present in the clipboard formats.
        """
        return {2}.intersection(format_ids)

    def execute(self, clipboard_element):
        if 2 in clipboard_element.get_format_ids():
            
            # Step 1: is script in official rembgProject ? No ? Copy that file
            project_base = self.configPlugin.read_option('project_base')
            script_base = self.configPlugin.read_option('base') 
            script_name = self.configPlugin.read_option('script_name')
            script_source = os.path.join(script_base, script_name)
            script_dest = os.path.join(project_base, script_name)

            if not os.path.exists(script_dest):
                try:
                    shutil.copyfile(script_source, script_dest)
                    print(f"Script '{script_name}' copié vers le projet rembg.")
                except Exception as e:
                    print(f"Erreur lors de la copie de '{script_name}' : {e}")
            else:
                print(f"Script '{script_name}' déjà présent dans le projet rembg.")

            # Step 2: Get file from lipboard and save in cache to process with rembg
            media = self.extract_image_from_clipboard()
            media.save(self.cache_save_path)


            # Step 3: Prepare input & output to process
            input_path = media.get_path()
            file_root, file_extension = os.path.splitext(input_path)
            output_path = f"{file_root}-rm{file_extension}"

                    
            # Step 4: Prepare the subprocess virtual environment
            venv_path = self.configPlugin.read_option('project_venv')   
            python_executable = os.path.join(venv_path, "Scripts", "python.exe")
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = venv_path
            env["PATH"] = os.path.join(venv_path, "Scripts") + ";" + env["PATH"]
            env["U2NET_HOME"] = self.configPlugin.read_option('U2NET_HOME')


            # Step 5: Call remote cliprembg.py using subprocess with venv project
            process = subprocess.run(
                [python_executable, script_dest, input_path, output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            if process.stderr:
                print(f"Error: {process.stderr}")
                exit()

            media.update_mimeType_path("image/png", output_path)

            return media

    def display_button(self):
        return "Rotoscope (IA)"