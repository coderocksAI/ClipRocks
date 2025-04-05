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

import win32clipboard

import ctypes
from ctypes.wintypes import HWND, UINT, HANDLE, BOOL
from typing import List

class ClipElement:
    """
    Represents an element in the clipboard, handling various formats such as text, files, and images.
    
    This class provides methods to interact with the clipboard, retrieve data in different formats,
    and perform operations like converting DIB data to PNG.
    """

    def __init__(self):
        """
        Initializes the ClipElement by retrieving current clipboard data.
        Automatically populates format_ids and media_info.
        """

        self.format_ids = self._retrieve_format_ids()
        self.raw_data = None  # Placeholder for raw clipboard data
        self.media_info = None  # Placeholder for future media information retrieval logic

        # Windows API constants
        self.CF_HDROP = 15

        # Load necessary Windows API functions
        self._is_clipboard_format_available = ctypes.windll.user32.IsClipboardFormatAvailable
        self._get_clipboard_data = ctypes.windll.user32.GetClipboardData
        self._open_clipboard = ctypes.windll.user32.OpenClipboard
        self._close_clipboard = ctypes.windll.user32.CloseClipboard
        self._drag_query_file = ctypes.windll.shell32.DragQueryFileW

        # Set function argument and return types
        self._is_clipboard_format_available.argtypes = [UINT]
        self._is_clipboard_format_available.restype = BOOL
        self._get_clipboard_data.argtypes = [UINT]
        self._get_clipboard_data.restype = HANDLE
        self._open_clipboard.argtypes = [HWND]
        self._open_clipboard.restype = BOOL
        self._close_clipboard.restype = BOOL
        self._drag_query_file.argtypes = [HANDLE, UINT, ctypes.c_wchar_p, UINT]
        self._drag_query_file.restype = UINT


    def get_copied_files(self):
        """
        Reads files copied to the clipboard.
        """
        if not self._open_clipboard(None):  # Ouvre le presse-papiers
            raise Exception("Unable to open the clipboard.")
        
        try:
            # Vérifie si le format CF_HDROP est disponible
            if not self._is_clipboard_format_available(self.CF_HDROP):
                print("No files found in the clipboard.")
                return []
            
            # Récupère le handle des données du presse-papiers
            handle = self._get_clipboard_data(self.CF_HDROP)
            if not handle:
                raise Exception("Error retrieving CF_HDROP data.")
            
            # Compte le nombre de fichiers
            num_files = self._drag_query_file(handle, 0xFFFFFFFF, None, 0)
            if num_files == 0:
                print("No files detected.")
                return []

            # Lit les chemins des fichiers
            files = []
            for i in range(num_files):
                buffer = ctypes.create_unicode_buffer(260)  # Buffer to store the path
                self._drag_query_file(handle, i, buffer, 260)
                files.append(buffer.value)
            
            return files
        finally:
            self._close_clipboard()  # Close the clipboard

    def _retrieve_format_ids(self):
        """
        Internal method to retrieve the format IDs from the clipboard.
        """
        formats = set()
        try:
            win32clipboard.OpenClipboard()
            format_id = win32clipboard.EnumClipboardFormats(0)
            while format_id != 0:
                formats.add(format_id)
                format_id = win32clipboard.EnumClipboardFormats(format_id)
        except Exception as e:
            print("Error: ", str(e))
        finally:
            win32clipboard.CloseClipboard()
        return formats

    def get_format_ids(self):
        """
        Getter for format_ids, ensuring it is only accessed after initialization.
        """
        return self.format_ids


    def get_raw_BITMAP(self):
        """
        Retrieves raw BITMAP data (CF_BITMAP) from the clipboard.
        """
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_BITMAP)
        except Exception as e:
            print("Error retrieving BITMAP data:", e)
            data = None
        finally:
            win32clipboard.CloseClipboard()
        return data

    def get_raw_DIB(self):
        """
        Retrieves raw DIB data (CF_DIB) from the clipboard.
        """
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
        except Exception as e:
            print("Error retrieving DIB data:", e)
            data = None
        finally:
            win32clipboard.CloseClipboard()
        return data

    def get_raw_UNICODETEXT(self):
        """
        Retrieves raw UNICODE text data (CF_UNICODETEXT) from the clipboard.
        """
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except Exception as e:
            print("Error retrieving UNICODE text data:", e)
            data = None
        finally:
            win32clipboard.CloseClipboard()
        return data


    def convert_to_png(self):
        """
        Converts raw clipboard data to a PNG image.
        """
        if self.raw_data is None:
            self._get_raw_data()

        if self.raw_data:
            try:
                # Convert DIB data to an image
                image = Image.open(io.BytesIO(self.raw_data))
                png_buffer = io.BytesIO()
                image.save(png_buffer, format="PNG")
                png_buffer.seek(0)
                return png_buffer  # Return as BytesIO for further use
            except Exception as e:
                print("Error converting to PNG:", e)
                return None
        return None

    def get_text(self):
        """
        Retrieves text data from the clipboard.
        """
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return text
        except Exception as e:
            print("Error retrieving text data:", e)
        finally:
            win32clipboard.CloseClipboard()

    def get_infos_media(self):
        """
        Placeholder for retrieving detailed media information for the clipboard element.
        """
        return {
            "format_ids": list(self.format_ids),
            "raw_data_available": self.raw_data is not None
        }

    def parse_hdrop_data(data: ctypes.c_void_p) -> List[str]:
        """
        Parses HDROP data type to extract file paths.
        
        Args:
            data (ctypes.c_void_p): The handle to the clipboard data of type CF_HDROP.

        Returns:
            List[str]: A list of file paths extracted from the clipboard data.
        """
        count = ctypes.windll.shell32.DragQueryFileW(data, -1, None, 0)
        files = []
        for i in range(count):
            length = ctypes.windll.shell32.DragQueryFileW(data, i, None, 0) + 1
            buffer = ctypes.create_unicode_buffer(length)
            ctypes.windll.shell32.DragQueryFileW(data, i, buffer, length)
            files.append(buffer.value)
            print(self.parse_hdrop_data.__doc__)
        return files