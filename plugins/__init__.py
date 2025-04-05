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
import os
import sys 
import importlib

for plugin_dir in os.listdir(os.path.dirname(__file__)):
    plugin_path = os.path.join(os.path.dirname(__file__), plugin_dir)
    if os.path.isdir(plugin_path):   # Checks if it's a directory
        main_file = os.path.join(plugin_path, "main.py")
        if os.path.isfile(main_file):   # Checks if main.py exists
            module_name = f"plugins.{plugin_dir}.main"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                print(f"Error importing plugin {module_name} : {e}")