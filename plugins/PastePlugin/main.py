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

class PastePlugin(PluginBase):
    def check_condition(self, format_ids):
        """
        Activates the plugin if CF_BITMAP (2) is present in the clipboard formats.
        """
        print(format_ids)
        return {1, 2, 15}.intersection(format_ids)

    def execute(self, clipboard_element):
        """
        Executes the plugin logic to paste the clipboard content into DaVinci Resolve.
        Handles images (CF_BITMAP) and text (CF_UNICODETEXT), including downloading content from URLs.
        """
        # Activer le venv principal
        # self.activate_shared_env()

        # option = self.getOption("myOption")
        # print(option)
        # exit()
        if 15 in clipboard_element.get_format_ids():
            print(clipboard_element.get_copied_files())
            exit()

        # CLIPBOARD TYPE IMAGE
        if 2 in clipboard_element.get_format_ids():
            return self.extract_image_from_clipboard()

        # CLIPBOARD TYPE TXT 
        elif 1 in clipboard_element.get_format_ids():
            text_data = clipboard_element.get_text()

            # TXT TYPE URL
            if self.is_url(text_data):

                custom_savers = { "text/url": self.save_download,}
                custom_catchers = { "text/url": self.catch_url, }

                return Media(
                        raw_content=text_data,
                        mime_type="text/url",
                        custom_savers=custom_savers,
                        custom_catchers=custom_catchers
                    )

            # Si ce n'est pas une URL, traiter comme du texte brut
            return Media(raw_content=text_data, mime_type="text/plain")

        raise ValueError("No compatible format found in clipboard.")

    def display_button(self):
        """
        Returns the name of the button to display in the UI.
        """

        return "Ajouter"

    def catch_url(self, media):
        """
        Downloads the content from the given URL.
        :return: (file_data, mime_type)
        """
        if not media.raw_content or not self.is_url(media.raw_content):
            raise ValueError("Invalid URL content provided.")
        
        #return media.raw_content

    def save_download(self, media):
        import os
        import mimetypes

        # 
        file_data, mime_type = self.download_file_from_url(media.raw_content)

        # Générer un nom de fichier basé sur le type MIME
        extension = mimetypes.guess_extension(mime_type) or ".bin"
        file_name = f"{media.index_file}{extension}"
        full_path = os.path.join(media.save_path, file_name)

        # Sauvegarder le contenu dans un fichier
        with open(full_path, "wb") as f:
            f.write(file_data)
        
        return extension.replace(".", ""), full_path