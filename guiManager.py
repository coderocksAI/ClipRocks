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


class GUIManager:
    def __init__(self, cliprocks):
        """
        Initializes the GUI Manager.
        """
        
        # Position the window at the position of the mouse
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

    def disable_close_focus_out(self):
        self.root.unbind("<FocusOut>")

    def enable_close_focus_out(self):
        self.root.bind("<FocusOut>", self.close_on_focus_out)

    def close_on_focus_out(self, event):
        print("declenchement du close_on_focus_out")
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
        self.root.destroy()