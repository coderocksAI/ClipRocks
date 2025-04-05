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

class DaVinciAPI:
    """
    A dedicated class for handling interactions with DaVinci Resolve's workspace,
    such as managing virtual folder (bins), timelines, and media pool operations.

    This class provides a comprehensive interface to interact with the media pool,
    create and manage bins, add media files to these bins, and integrate them into
    timelines within DaVinci Resolve. It encapsulates common functionalities
    related to media management and project settings.
    """

    def __init__(self, resolve, binName):
        """
        Initialize the workspace with the media pool.
        """

        """──────────────────────────────────────────────────────────────────────────────────
        Initialize DaVinci Resolve API 
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        # Initialize DaVinci Resolve objects
        self.resolve = resolve
        self.project_manager = self.resolve.GetProjectManager()
        self.current_project = self.project_manager.GetCurrentProject()
        self.media_pool = self.current_project.GetMediaPool()
        self.media_storage = resolve.GetMediaStorage()

        """──────────────────────────────────────────────────────────────────────────────────
        Configuration DaVinci Resolve 
        ─▼─────────────────────────────────────────────────────────────────────────────▼──"""

        # nom du dossier virtuel
        self.binName = binName

        # Project-specific settings
        self.project_name = self.current_project.GetName()
        self.project_settings = self.current_project.GetSetting()
        # self.media_pool = media_pool

    def _create_bin(self, rootFolder):
        """
        Create the virtual folder bin in the media pool. `__ClipRocks__`
        :param rootFolder: The root folder of the media pool.
        :return: The newly created media pool folder object.
        """
        self.media_pool.AddSubFolder(rootFolder, self.binName)
        return self._get_bin_if_exists(rootFolder)

    def get_or_create_bin(self):
        """
        Retrieve the `__ClipRocks__` bin or create it if it doesn't exist.
        """
        rootFolder = self.media_pool.GetRootFolder()
        binFolder = self._get_bin_if_exists(rootFolder)
        if not binFolder:
            binFolder = self._create_bin(rootFolder)
        return binFolder

    def _get_bin_if_exists(self, rootFolder):
        """
        Check and get if the `__ClipRocks__` bin already exists in GUI.
        """
        for folder in rootFolder.GetSubFolderList():
            if folder.GetName() == self.binName:
                return folder
        return None

        
    def add_to_bin(self, binFolder, file_path):
        """
        Adds a file to the __ClipRocks__ bin in DaVinci Resolve.
        !!!Note : AddItemsToMediaPool considers the case of the path when verifying accuracy!
        (2) CONFIGURE THE PATH IN MEDIA STORAGE (can be removed from preferences) Todo: automatic addition.
        """
        self.media_pool.SetCurrentFolder(binFolder)
        return self.media_storage.AddItemsToMediaPool(file_path)

    def get_item_by_name(self, clips, clip_name):
        """
        Find a media pool item by its name.
        :param clips: List of clips in the media pool.
        :param clip_name: Name of the clip to find.
        :return: The matching media pool item, or None if not found.
        """
        for clip in clips:
            if clip.GetName() == clip_name:
                return clip
        return None

    def add_to_timeline(self, subClip):
        """
        Add a media pool item to the timeline.
        :param media_pool_item: The media pool item to add.
        :param start_frame: Optional starting frame for the clip.
        :param end_frame: Optional ending frame for the clip.
        :param frame: Optional frame for a specific position in the timeline.
        """
        return self.media_pool.AppendToTimeline(subClip)

    def getCurrentProjectSettings(self, name):
        """
        Retrieve the value of a specific setting in the current project.
        :param name: Name of the project setting to retrieve.
        :return: The value of the requested setting.
        """
        return self.current_project.GetSetting(name)

    def getCurrentProjectName(self):
        """
        Retrieve the name of the current project.
        :return: The name of the current project as a string.
        """
        return self.current_project.GetName()

    def getCurrentFolder(self):
        """
        Retrieve the currently selected folder in the media pool.
        :return: The currently selected media pool folder object.
        """
        return self.media_pool.GetCurrentFolder()
