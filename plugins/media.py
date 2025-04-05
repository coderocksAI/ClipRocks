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
import io
import win32clipboard
from PIL import Image # Convert the handle to actual image data


class Media:
    def __init__(self, raw_content=None, mime_type=None, path=None, custom_savers={}, custom_catchers={}):
        """
        TODO: Consider implementing a history of mutations with a table of paths to be able to trace 
        its processing and dependencies in case of consultation, modification, or complete deletion.

        A media is defined by its origin `path` and destination `path_save`. These elements can be updated with
        each processing step, leading to an infinite number of possible mutations. 
         
        Note: Be cautious, as a media will leave traces of these different saved files on the disk throughout its 
        mutations. 

        The `custom_savers` and `custom_catchers` allow for flexible handling of media content. Custom savers are
        functions that take the raw content and save it to a specific location, while custom catchers are functions
        that pre-process the raw content before it is saved or displayed. (See example PastePlugin).        
        """

        # defined only after saved. (ex: index_file+ext : 5.png).
        self.filename = None
        
        # auto increment number as name 
        self.index_file = None

        # Content from clipboard
        self.raw_content = raw_content

        # defined for _default or custom savers/catchers
        self.mime_type = mime_type

        # defined/updated when file ALREADY SAVED or mime_type updated.
        # behavior can be different if media is cliboard or real file with path (is None ?)
        self.path = path

        # defined FOR SAVE before stored
        self.save_path = None


        """──────────────────────────────────────────────────────────────────────────────────
        Catchers & Savers 
            Save() -> _get_catcher() -> "mime/type" : self_method
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        self.custom_catchers = custom_catchers
        self.custom_savers = custom_savers

        self._default_savers = {
            "image/png": self._save_as_image,
            "text/plain": self._save_as_text,
            "video/mp4": self._save_as_video,
        }

        self._default_catchers = {
            "image/png": self._get_content_image,
            "text/plain": self._get_content_text,
            "video/mp4": self._get_content_video,
        }



    def save(self, save_path):
        """
        Saves the media using the appropriate saver.   

        If `self.path` is defined, the media will be processed from real file. Otherwise, 
        we get raw content from the clipboard. finally we store to the specified `save_path`.
        
        After saving, the method updates the `path`, `filename`, and `index_file`. The media are
        not clipboard anymore because self.path not None. 
        """

        self.save_path = save_path
        catcher = self._get_catcher()
        saver = self._get_saver()
        
        if not catcher or not saver:
            raise ValueError(f"No saver available for MIME type: {self.mime_type}")

        # wtf I added self ? circular injection ?? 
        catcher(self)

        self.index_file = self._generate_file_name(self.save_path)
        extension, self.path = saver(self)
        self.filename = f"{self.index_file}.{extension}"
        
        return self.path


    def _get_catcher(self):
        """
        Retrieves the appropriate catcher based on the MIME type.

        This method checks for a custom catcher first. If no custom catcher is found,
        it falls back to the default catchers defined in `_default_catchers`. 
        Returns None if no catcher is available for the specified MIME type.
        """
        catchers = {**self._default_catchers, **self.custom_catchers}
        return catchers.get(self.mime_type)


    def _get_content_image(self, media):
        """
        Load image from the file path if `self.path` exists. Else, it retrieves the 
        image from the clipboard.
        
        Note:
            - The image is returned as a PIL.Image object for further processing or display.
            - This method ensures that the image content is correctly loaded, handling both clipboard
              data and files on disk.
        """
        if self.path:
            folder = os.path.dirname(self.path)
            if os.path.exists(folder):
                with open(self.path, 'rb') as f:
                    raw_data = f.read() 
                    self.raw_content = Image.open(io.BytesIO(raw_data))  # Charge le fichier comme une image PIL
                    return
        self.raw_content = self.get_clipboard_image()  # Retourne l'image depuis le presse-papier


    def _get_content_text(self, media):
        """
        Retrieves text content either from the clipboard or from the existing file path.
        :return: Raw text content.
        """
        # if self.path and os.path.exists(self.path):
        #     with open(self.path, 'r', encoding="utf-8") as f:
        #         return f.read()
        # self.raw_content = self.get_raw_UNICODETEXT()
        print("Fonctionnalité non gérée pour l'instant")
        exit() 



    def _get_content_video(self):
        """
        Retrieves video content from an existing `self.path` 
        Note: Currently, clipboard support for videos is not available in this implementation.
        :return: Raw video content.
        """
        if self.path and os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                return f.read()
        raise ValueError("Video content must come from an existing file path.")


    def get_filename(self):
        """
        get the media filename (index_file + ext)
        example : `14.png`
        """
        if not self.filename:
            raise ValueError("Media has not been saved yet; filename is unavailable.")
        return self.filename

    def get_path(self):
        """
        Returns the current  of the media (or None if media are in clipboard). alwayse the last
        current file path from the media saved by current last process.
        """
        return self.path

    def update_mimeType_path(self, mimeType, path):
        """
        Updates the MIME type and path for the media.

        TODO : For now, we need to update the path. This is not a good behavior. Save has the 
        responsibility for paths. Why not move the updateMimeTypePath method to be used in the 
        save method?
        """
        self.mime_type = mimeType
        self.path = path
        
    def _get_saver(self):
        """
        Retrieves the appropriate saver, prioritizing custom savers.
        Return The appropriate saver method or None if no suitable saver is found.
        """
         # Merges default and custom savers; custom can overwrite default 
        savers = {**self._default_savers, **self.custom_savers}
        return savers.get(self.mime_type)


    def _save_as_image(self, media):
        """
        Saves an image to the specified path using the provided raw content.
        :return: Tuple (file extension, full path to the saved file).

        TODO : Why I did that (self, media) ??? Very strange, investigation is required
        """
        file_name = f"{self.index_file}.png"
        full_path = os.path.join(self.save_path, file_name)
        # Sauvegarde l'image
        self.raw_content.save(full_path)  # Enregistre directement l'image PIL
        return "png", full_path


    def _save_as_text(self, media):
        print("Functionality not handled for now")
        exit() 

    def _save_as_video(self, raw_content, save_path, index_file):
        """
        Saves the given raw content as a video file.

        Todo: Make the file format flexible so it can save files 
        in other formats besides MP4.
        """
        file_name = f"{index_file}.{"mp4"}"
        full_path = os.path.join(save_path, file_name)
        with open(full_path, "wb") as f:
            f.write(raw_content)
        return "mp4", full_path

    def _generate_file_name(self, save_path):
        """
        Generates a unique file name by finding the next available index in the given save path.
        
        TODO : May be optimized by static incremental propertie ID without list ? What happen when 
        hundreds files ? or delete last files and decrement ?
        """
        existing_files = os.listdir(save_path)
        next_index = max(
            [int(f.split('.')[0]) for f in existing_files if f.split('.')[0].isdigit()],
            default=0
        ) + 1
        return next_index

    def get_clipboard_image(self):
        """
        Get an image from the clipboard and returns it as a PIL Image object.
        Returns the image if available, otherwise None.
        """
        win32clipboard.OpenClipboard()
        try:
            # Check if an image is available
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                 # Convert the DIB (Device Independent Bitmap) data to a PIL Image
                stream = io.BytesIO(data)
                image = Image.open(stream)
                return image
            else:
                print("No image in clipboard.")
                return None
        finally:
            win32clipboard.CloseClipboard()