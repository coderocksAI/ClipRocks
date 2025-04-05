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
import sys
import subprocess

class VirtualEnvHelper:
    """
    Helper class for managing virtual environments.
    Provides methods to activate a virtual environment for the current process or subprocesses.
    """

    def __init__(self, venv_path):
        """
        Initializes the VirtualEnvHelper with the path to the virtual environment.

        :param venv_path: Path to the virtual environment.
        """
        self.venv_path = venv_path
        self.site_packages = os.path.join(venv_path, "Lib", "site-packages")
        self.python_executable = os.path.join(venv_path, "Scripts", "python.exe")  # Adjust for Linux/Mac if needed

    def activate_for_current_process(self):
        """
        Activates the virtual environment for the current Python process.
        
        This method modifies the `sys.path` and `os.environ` to include the virtual environment's site-packages
        and python executable, respectively. It ensures that any further imports use the packages installed in the
        virtual environment.
        """
        if not os.path.exists(self.site_packages):
            raise FileNotFoundError(f"Site-packages not found in virtual environment: {self.site_packages}")
        sys.path.insert(0, self.site_packages)
        os.environ["VIRTUAL_ENV"] = self.venv_path
        os.environ["PATH"] = os.path.join(self.venv_path, "Scripts") + ";" + os.environ["PATH"]

        # print(os.environ["VIRTUAL_ENV"])

        # print(os.environ["PATH"])

        # print(f"sys.path: {sys.path}")
        # print(f"sys.executable: {sys.executable}")
        # import urllib3
        # http = urllib3.PoolManager()
        # response = http.request('GET', 'https://www.example.com')
        # print(f"Test urllib3: Status {response.status}")
        # exit()

    def initVirtualEnv(self):
        """
        Initializes the virtual environment for the current process.
        
        This method calls `activate_for_current_process` and returns a reference to
        itself, ensuring that further operations can be chained on the same instance.
        """
        try:
            self.activate_for_current_process()
            return self
        except Exception as e:
            raise RuntimeError(f"Failed to initialize virtual environment at {self.venv_path}. Error: {e}")

    def prepare_for_subprocess(self):
        """
        Prepares the environment for subprocess execution with the virtual environment.
        
        This method creates a copy of the current environment variables, modifies them 
        to include the virtual environment's site-packages and python executable, and 
        returns the modified environment dictionary.
        """
        if not os.path.exists(self.python_executable):
            raise FileNotFoundError(f"Python executable not found in virtual environment: {self.python_executable}")
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = self.venv_path
        env["PATH"] = os.path.join(self.venv_path, "Scripts") + ";" + env["PATH"]
        return env

    def run_script_in_venv(self, script_path, *args):
        """
        Runs a Python script in the virtual environment using subprocess.

        This method uses the prepared environment to execute a given Python 
        script with any additional arguments.
        
        :param script_path: Path to the script to execute.
        :param args: Additional arguments to pass to the script.
        :return: The subprocess.Popen object.
        """
        env = self.prepare_for_subprocess()
        return subprocess.Popen(
            [self.python_executable, script_path, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

# Example usage:
# helper = VirtualEnvHelper("path/to/venv")
# helper.activate_for_current_process()  # For ResolveAI
# env = helper.prepare_for_subprocess()  # For subprocess
