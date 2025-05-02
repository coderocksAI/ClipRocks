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
import tkinter as tk
import win32api     
from tkinter import messagebox

class GUIManager:
    def __init__(self, cliprocks):
        """
        Initializes the GUI Manager.
        """
        
        # define x,y window at the location of the mouse
        self.mouse = win32api.GetCursorPos()

        self.cliprocks = cliprocks
        self.root = tk.Tk()
        self.root.title("ClipRocks Plugins")
        self.root.geometry(f"+{self.mouse[0]}+{self.mouse[1]}")

        self.root.config(width=100)
        self.root.configure(bg="#282828")

        self.root.overrideredirect(True)  
        self.enable_close_focus_out()

        self.button_frame = tk.Frame(self.root, bg="#282828")
        self.button_frame.pack(fill=tk.BOTH, expand=True)


    def show_install_dialog(self, venvPath):
        # Show a dialog box
        response = messagebox.askyesno(
            title="Missing Modules",
            message=(
                "The expected Python modules virtual folder is not found :\n\n"
                f"{venvPath}\n\n"
                "To install them manually, follow these steps in a command prompt:\n\n"
                f"1. cd /d \"{venvPath}\"\n"
                "2. python -m venv venv\n"
                "3. venv\\Scripts\\activate\n"
                "4. pip install pillow requests\n\n"
                "Do you want to learn more by visiting the project's GitHub page?"
            )
        )
        return response


    def disable_close_focus_out(self):
        """
        Disables the automatic closure of the window when it loses focus. This 
        method unbinds the "<FocusOut>" event from the root widget, preventing the
        window from being closed when the user clicks outside of it. Use this 
        method to revert the behavior set by `enable_close_focus_out()` if needed.
        """
        self.root.unbind("<FocusOut>")

    def enable_close_focus_out(self):
        """
        Enables the automatic closure of the window when it loses focus.  This method 
        binds the "<FocusOut>" event to the `close_on_focus_out` method, causing the 
        window to be closed when the user clicks outside of it. Use this method if you
        want the application to automatically close the window on a focus out event.
        To disable this behavior, use the `disable_close_focus_out()` method.
        """
        self.root.bind("<FocusOut>", self.close_on_focus_out)

    def close_on_focus_out(self, event):
        """
        Closes the window when it loses focus. This method is used to automatically 
        close a window when the user clicks outside of it. However, be cautious when
        creating new windows, as this can inadvertently trigger a focus out event 
        and cause an unintended closure of the application. To disable this behavior,
        use the `disable_close_focus_out()` method.
        """
        event.widget.destroy()
        exit(0)

    def add_button(self, button_name, plugin_instance):
        """
        Adds a button dynamically to the GUI.
        """
        def on_click():
            self.cliprocks.on_button_click(button_name)

        button = tk.Button(
            self.button_frame,
            text=button_name,
            command=on_click,
            bg="#181818",
            fg="white",
            activebackground="#383838",
            activeforeground="white"
        )
        button.pack(pady=5, padx=10)

    def run(self):
        """
        Starts the Tkinter main loop.
        """
        self.root.mainloop()

    def exit(self):
        """
        Closes or destroys the main window associated with the GUI managed by this instance.
        """
        self.root.destroy()