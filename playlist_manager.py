#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Playlist management module for creating, loading, and managing playlists
"""

import os
import json
import uuid
import random
import datetime
from typing import List, Dict, Optional, Any, Union, Tuple, Callable
from enum import Enum, auto
from PyQt5.QtCore import QObject, pyqtSignal

from metadata_handler import MetadataHandler


class RepeatMode(Enum):
    """Enumeration for playlist repeat modes."""
    NO_REPEAT = auto()  # Play through playlist once
    REPEAT_PLAYLIST = auto()  # Repeat the entire playlist
    REPEAT_TRACK = auto()  # Repeat the current track


class PlaylistFormat(Enum):
    """Enumeration for supported playlist file formats."""
    JSON = auto()  # Custom JSON format
    M3U = auto()  # M3U format
    PLS = auto()  # PLS format


class Track:
    """
    Represents a single track in a playlist with its metadata.
    """
    
    def __init__(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a track.
        
        Args:
            file_path (str): Path to the audio file
            metadata (Optional[Dict[str, Any]]): Pre-loaded metadata, if available
        """
        self.file_path = file_path
        self.metadata = metadata or {}
        self.uuid = str(uuid.uuid4())  # Unique identifier for this track instance
    
    def __eq__(self, other: object) -> bool:
        """
        Check if two track objects are equal.
        
        Args:
            other (object): Another track object to compare with
            
        Returns:
            bool: True if the tracks are equal, False otherwise
        """
        if not isinstance(other, Track):
            return False
        
        return self.uuid == other.uuid
    
    def __repr__(self) -> str:
        """
        Get a string representation of the track.
        
        Returns:
            str: String representation
        """
        title = self.metadata.get('title', os.path.basename(self.file_path))
        artist = self.metadata.get('artist', 'Unknown Artist')
        return f"{title} - {artist}"


class Playlist:
    """
    Represents a playlist with tracks and metadata.
    """
    
    def __init__(self, name: str, tracks: Optional[List[Track]] = None) -> None:
        """
        Initialize a playlist.
        
        Args:
            name (str): Name of the playlist
            tracks (Optional[List[Track]]): Initial list of tracks, if any
        """
        self.name = name
        self.tracks = tracks or []
        self.uuid = str(uuid.uuid4())  # Unique identifier for this playlist instance
        self.creation_date = datetime.datetime.now().isoformat()
        self.last_modified = self.creation_date
        self.description = ""
        self.custom_metadata: Dict[str, Any] = {}
    
    def add_track(self, track: Track) -> None:
        """
        Add a track to the playlist.
        
        Args:
            track (Track): Track to add
        """
        self.tracks.append(track)
        self.last_modified = datetime.datetime.now().isoformat()
    
    def remove_track(self, index: int) -> Optional[Track]:
        """
        Remove a track from the playlist.
        
        Args:
            index (int): Index of the track to remove
            
        Returns:
            Optional[Track]: The removed track, or None if the index is invalid
        """
        if 0 <= index < len(self.tracks):
            track = self.tracks.pop(index)
            self.last_modified = datetime.datetime.now().isoformat()
            return track
        return None
    
    def move_track(self, from_index: int, to_index: int) -> bool:
        """
        Move a track from one position to another.
        
        Args:
            from_index (int): Current index of the track
            to_index (int): New index for the track
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= from_index < len(self.tracks) and 0 <= to_index < len(self.tracks):
            track = self.tracks.pop(from_index)
            self.tracks.insert(to_index, track)
            self.last_modified = datetime.datetime.now().isoformat()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all tracks from the playlist."""
        self.tracks = []
        self.last_modified = datetime.datetime.now().isoformat()
    
    def get_total_duration(self) -> int:
        """
        Get the total duration of the playlist in milliseconds.
        
        Returns:
            int: Total duration in milliseconds
        """
        total = 0
        for track in self.tracks:
            duration = track.metadata.get('duration', 0)
            if isinstance(duration, int):
                total += duration
        return total
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get playlist statistics.
        
        Returns:
            Dict[str, Any]: Dictionary with playlist statistics
        """
        total_duration = self.get_total_duration()
        return {
            'name': self.name,
            'track_count': len(self.tracks),
            'total_duration': total_duration,
            'total_duration_str': self._format_duration(total_duration // 1000),  # Convert ms to seconds
            'creation_date': self.creation_date,
            'last_modified': self.last_modified,
        }
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """
        Format duration in seconds to a human-readable string.
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration string (HH:MM:SS or MM:SS)
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the playlist to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the playlist
        """
        return {
            'name': self.name,
            'uuid': self.uuid,
            'creation_date': self.creation_date,
            'last_modified': self.last_modified,
            'description': self.description,
            'custom_metadata': self.custom_metadata,
            'tracks': [
                {
                    'file_path': track.file_path,
                    'uuid': track.uuid,
                    # Only store minimal metadata to avoid redundancy
                    'title': track.metadata.get('title'),
                    'artist': track.metadata.get('artist'),
                    'album': track.metadata.get('album'),
                    'duration': track.metadata.get('duration'),
                }
                for track in self.tracks
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Playlist':
        """
        Create a playlist from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary representation of a playlist
            
        Returns:
            Playlist: New playlist instance
        """
        playlist = cls(data['name'])
        playlist.uuid = data.get('uuid', str(uuid.uuid4()))
        playlist.creation_date = data.get('creation_date', datetime.datetime.now().isoformat())
        playlist.last_modified = data.get('last_modified', playlist.creation_date)
        playlist.description = data.get('description', '')
        playlist.custom_metadata = data.get('custom_metadata', {})
        
        for track_data in data.get('tracks', []):
            track = Track(track_data['file_path'])
            track.uuid = track_data.get('uuid', str(uuid.uuid4()))
            
            # Initialize with minimal metadata until we need full metadata
            track.metadata = {
                'title': track_data.get('title'),
                'artist': track_data.get('artist'),
                'album': track_data.get('album'),
                'duration': track_data.get('duration'),
            }
            
            playlist.tracks.append(track)
        
        return playlist


class PlaylistManager(QObject):
    """
    Manages playlists for the Radar Whisper application.
    Handles creating, loading, saving, and manipulating playlists.
    """
    
    # Define signals for communication with UI
    playlist_changed = pyqtSignal(str)  # Playlist UUID
    current_track_changed = pyqtSignal(int)  # Track index
    playlist_loaded = pyqtSignal(str)  # Playlist UUID
    playlist_saved = pyqtSignal(str)  # Playlist UUID
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self, metadata_handler: Optional[MetadataHandler] = None) -> None:
        """
        Initialize the playlist manager.
        
        Args:
            metadata_handler (Optional[MetadataHandler]): MetadataHandler instance for retrieving track metadata
        """
        super().__init__()
        
        self._metadata_handler = metadata_handler or MetadataHandler()
        self._playlists: Dict[str, Playlist] = {}  # UUID -> Playlist
        self._current_playlist_uuid: Optional[str] = None
        self._current_track_index: int = -1
        self._shuffle_mode: bool = False
        self._repeat_mode: RepeatMode = RepeatMode.NO_REPEAT
        self._shuffle_history: List[int] = []
        self._shuffle_index: int = -1
    
    def create_playlist(self, name: str) -> str:
        """
        Create a new empty playlist.
        
        Args:
            name (str): Name of the playlist
            
        Returns:
            str: UUID of the new playlist
        """
        playlist = Playlist(name)
        self._playlists[playlist.uuid] = playlist
        
        # If this is the first playlist, set it as current
        if len(self._playlists) == 1:
            self._current_playlist_uuid = playlist.uuid
        
        self.playlist_changed.emit(playlist.uuid)
        return playlist.uuid
    
    def get_playlist(self, uuid: str) -> Optional[Playlist]:
        """
        Get a playlist by UUID.
        
        Args:
            uuid (str): UUID of the playlist
            
        Returns:
            Optional[Playlist]: The playlist, or None if not found
        """
        return self._playlists.get(uuid)
    
    def get_current_playlist(self) -> Optional[Playlist]:
        """
        Get the current playlist.
        
        Returns:
            Optional[Playlist]: The current playlist, or None if no playlist is selected
        """
        if self._current_playlist_uuid:
            return self._playlists.get(self._current_playlist_uuid)
        return None
    
    def set_current_playlist(self, uuid: str) -> bool:
        """
        Set the current playlist.
        
        Args:
            uuid (str): UUID of the playlist
            
        Returns:
            bool: True if successful, False if the playlist doesn't exist
        """
        if uuid in self._playlists:
            self._current_playlist_uuid = uuid
            self._current_track_index = -1
            self._shuffle_history = []
            self._shuffle_index = -1
            self.playlist_changed.emit(uuid)
            return True
        return False
    
    def get_all_playlists(self) -> List[Playlist]:
        """
        Get all playlists.
        
        Returns:
            List[Playlist]: List of all playlists
        """
        return list(self._playlists.values())
    
    def delete_playlist(self, uuid: str) -> bool:
        """
        Delete a playlist.
        
        Args:
            uuid (str): UUID of the playlist
            
        Returns:
            bool: True if successful, False if the playlist doesn't exist
        """
        if uuid in self._playlists:
            del self._playlists[uuid]
            
            # If we deleted the current playlist, select another one if available
            if uuid == self._current_playlist_uuid:
                if self._playlists:
                    self._current_playlist_uuid = next(iter(self._playlists.keys()))
                else:
                    self._current_playlist_uuid = None
                self._current_track_index = -1
                self._shuffle_history = []
                self._shuffle_index = -1
            
            self.playlist_changed.emit(uuid)
            return True
        return False
    
    def add_track_to_playlist(self, uuid: str, file_path: str) -> bool:
        """
        Add a track to a playlist.
        
        Args:
            uuid (str): UUID of the playlist
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        playlist = self._playlists.get(uuid)
        if not playlist:
            return False
        
        try:
            # Get metadata for the track
            metadata = self._metadata_handler.get_metadata(file_path)
            track = Track(file_path, metadata)
            playlist.add_track(track)
            self.playlist_changed.emit(uuid)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error adding track: {str(e)}")
            return False
    
    def add_tracks_to_playlist(self, uuid: str, file_paths: List[str]) -> int:
        """
        Add multiple tracks to a playlist.
        
        Args:
            uuid (str): UUID of the playlist
            file_paths (List[str]): List of paths to audio files
            
        Returns:
            int: Number of tracks successfully added
        """
        playlist = self._playlists.get(uuid)
        if not playlist:
            return 0
        
        success_count = 0
        for file_path in file_paths:
            try:
                # Process in batches if needed to improve performance
                metadata = self._metadata_handler.get_metadata(file_path)
                track = Track(file_path, metadata)
                playlist.add_track(track)
                success_count += 1
            except Exception as e:
                self.error_occurred.emit(f"Error adding track {file_path}: {str(e)}")
        
        if success_count > 0:
            self.playlist_changed.emit(uuid)
        
        return success_count
    
    def remove_track_from_playlist(self, uuid: str, index: int) -> bool:
        """
        Remove a track from a playlist.
        
        Args:
            uuid (str): UUID of the playlist
            index (int): Index of the track to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        playlist = self._playlists.get(uuid)
        if not playlist:
            return False
        
        removed_track = playlist.remove_track(index)
        if removed_track:
            # If we removed the current track, reset the current index
            if uuid == self._current_playlist_uuid and index == self._current_track_index:
                self._current_track_index = -1
                self.current_track_changed.emit(-1)
            # If we removed a track before the current track, adjust the index
            elif uuid == self._current_playlist_uuid and index < self._current_track_index:
                self._current_track_index -= 1
                self.current_track_changed.emit(self._current_track_index)
            
            self.playlist_changed.emit(uuid)
            return True
        
        return False
    
    def get_current_track(self) -> Optional[Tuple[Track, int]]:
        """
        Get the current track and its index.
        
        Returns:
            Optional[Tuple[Track, int]]: Tuple of (track, index), or None if no track is selected
        """
        playlist = self.get_current_playlist()
        if not playlist or self._current_track_index < 0 or self._current_track_index >= len(playlist.tracks):
            return None
        
        return (playlist.tracks[self._current_track_index], self._current_track_index)
    
    def set_current_track(self, index: int) -> bool:
        """
        Set the current track.
        
        Args:
            index (int): Index of the track to set as current
            
        Returns:
            bool: True if successful, False otherwise
        """
        playlist = self.get_current_playlist()
        if not playlist or index < 0 or index >= len(playlist.tracks):
            return False
        
        self._current_track_index = index
        self._shuffle_index = self._shuffle_history.index(index) if index in self._shuffle_history else -1
        self.current_track_changed.emit(index)
        return True
    
    def get_next_track(self) -> Optional[Tuple[Track, int]]:
        """
        Get the next track and its index based on current settings (shuffle, repeat).
        
        Returns:
            Optional[Tuple[Track, int]]: Tuple of (track, index), or None if no next track is available
        """
        playlist = self.get_current_playlist()
        if not playlist or not playlist.tracks:
            return None
        
        next_index = -1
        
        if self._shuffle_mode:
            next_index = self._get_next_shuffle_index()
        else:
            # Normal sequential playback
            next_index = self._current_track_index + 1
            
            # If we're at the end, handle repeat mode
            if next_index >= len(playlist.tracks):
                if self._repeat_mode == RepeatMode.REPEAT_PLAYLIST:
                    next_index = 0
                elif self._repeat_mode == RepeatMode.REPEAT_TRACK:
                    next_index = self._current_track_index
                else:
                    # No repeat, we've reached the end
                    return None
        
        if next_index >= 0 and next_index < len(playlist.tracks):
            self._current_track_index = next_index
            self.current_track_changed.emit(next_index)
            return (playlist.tracks[next_index], next_index)
        
        return None
    
    def get_previous_track(self) -> Optional[Tuple[Track, int]]:
        """
        Get the previous track and its index based on current settings.
        
        Returns:
            Optional[Tuple[Track, int]]: Tuple of (track, index), or None if no previous track is available
        """
        playlist = self.get_current_playlist()
        if not playlist or not playlist.tracks:
            return None
        
        prev_index = -1
        
        if self._shuffle_mode:
            # In shuffle mode, go back in the shuffle history
            if self._shuffle_index > 0:
                self._shuffle_index -= 1
                prev_index = self._shuffle_history[self._shuffle_index]
            elif self._repeat_mode == RepeatMode.REPEAT_PLAYLIST:
                # If repeating, wrap around to the end of the shuffle history
                self._shuffle_index = len(self._shuffle_history) - 1
                prev_index = self._shuffle_history[self._shuffle_index]
            else:
                # Stay at the beginning if not repeating
                prev_index = self._current_track_index
        else:
            # Normal sequential playback
            prev_index = self._current_track_index - 1
            
            # If we're at the beginning, handle repeat mode
            if prev_index < 0:
                if self._repeat_mode == RepeatMode.REPEAT_PLAYLIST:
                    prev_index = len(playlist.tracks) - 1
                elif self._repeat_mode == RepeatMode.REPEAT_TRACK:
                    prev_index = self._current_track_index
                else:
                    # No repeat, we've reached the beginning
                    return None
        
        if prev_index >= 0 and prev_index < len(playlist.tracks):
            self._current_track_index = prev_index
            self.current_track_changed.emit(prev_index)
            return (playlist.tracks[prev_index], prev_index)
        
        return None
    
    def set_shuffle_mode(self, enabled: bool) -> None:
        """
        Set the shuffle mode.
        
        Args:
            enabled (bool): True to enable shuffle mode, False to disable
        """
        if self._shuffle_mode != enabled:
            self._shuffle_mode = enabled
            
            if enabled:
                # Generate a new shuffle order
                self._generate_shuffle_order()
            else:
                # Clear shuffle history but keep current track
                self._shuffle_history = []
                self._shuffle_index = -1
    
    def set_repeat_mode(self, mode: RepeatMode) -> None:
        """
        Set the repeat mode.
        
        Args:
            mode (RepeatMode): The repeat mode to set
        """
        self._repeat_mode = mode
    
    def _generate_shuffle_order(self) -> None:
        """Generate a new random order for shuffle mode."""
        playlist = self.get_current_playlist()
        if not playlist or not playlist.tracks:
            self._shuffle_history = []
            self._shuffle_index = -1
            return
        
        # Create a list of all indices
        indices = list(range(len(playlist.tracks)))
        
        # If we have a current track, start with it
        if self._current_track_index >= 0:
            # Remove the current track from the list
            if self._current_track_index in indices:
                indices.remove(self._current_track_index)
            
            # Shuffle the remaining tracks
            random.shuffle(indices)
            
            # Put the current track at the beginning
            self._shuffle_history = [self._current_track_index] + indices
            self._shuffle_index = 0
        else:
            # No current track, just shuffle all tracks
            random.shuffle(indices)
            self._shuffle_history = indices
            self._shuffle_index = -1
    
    def _get_next_shuffle_index(self) -> int:
        """
        Get the next index in shuffle mode.
        
        Returns:
            int: Next track index, or -1 if no next track is available
        """
        # If we have no shuffle history or current playlist, regenerate
        if not self._shuffle_history or not self.get_current_playlist():
            self._generate_shuffle_order()
            
            # Still nothing? Return -1
            if not self._shuffle_history:
                return -1
        
        # If we're not in the shuffle history yet, start at the beginning
        if self._shuffle_index < 0:
            self._shuffle_index = 0
            return self._shuffle_history[0]
        
        # Move to the next index
        self._shuffle_index += 1
        
        # If we're at the end, handle repeat mode
        if self._shuffle_index >= len(self._shuffle_history):
            if self._repeat_mode == RepeatMode.REPEAT_PLAYLIST:
                # Generate a new shuffle order to avoid repeating the same order
                self._generate_shuffle_order()
                self._shuffle_index = 0
                return self._shuffle_history[0]
            elif self._repeat_mode == RepeatMode.REPEAT_TRACK:
                # Repeat the current track
                self._shuffle_index -= 1
                return self._shuffle_history[self._shuffle_index]
            else:
                # No repeat, we've reached the end
                self._shuffle_index = len(self._shuffle_history) - 1
                return -1
        
        return self._shuffle_history[self._shuffle_index]
    
    def save_playlist(self, uuid: str, file_path: str, format: PlaylistFormat = PlaylistFormat.JSON) -> bool:
        """
        Save a playlist to a file.
        
        Args:
            uuid (str): UUID of the playlist
            file_path (str): Path where the playlist should be saved
            format (PlaylistFormat): Format to save the playlist in
            
        Returns:
            bool: True if successful, False otherwise
        """
        playlist = self._playlists.get(uuid)
        if not playlist:
            self.error_occurred.emit(f"Playlist with UUID {uuid} not found")
            return False
        
        try:
            if format == PlaylistFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(playlist.to_dict(), f, indent=2)
            elif format == PlaylistFormat.M3U:
                return self._save_as_m3u(playlist, file_path)
            elif format == PlaylistFormat.PLS:
                return self._save_as_pls(playlist, file_path)
            else:
                self.error_occurred.emit(f"Unsupported playlist format: {format}")
                return False
            
            self.playlist_saved.emit(uuid)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error saving playlist: {str(e)}")
            return False
    
    def load_playlist(self, file_path: str, format: Optional[PlaylistFormat] = None) -> Optional[str]:
        """
        Load a playlist from a file.
        
        Args:
            file_path (str): Path to the playlist file
            format (Optional[PlaylistFormat]): Format of the playlist file, or None to auto-detect
            
        Returns:
            Optional[str]: UUID of the loaded playlist, or None if loading failed
        """
        if not os.path.exists(file_path):
            self.error_occurred.emit(f"Playlist file not found: {file_path}")
            return None
        
        # Auto-detect format if not specified
        if format is None:
            _, ext = os.path.splitext(file_path.lower())
            if ext == '.json':
                format = PlaylistFormat.JSON
            elif ext == '.m3u' or ext == '.m3u8':
                format = PlaylistFormat.M3U
            elif ext == '.pls':
                format = PlaylistFormat.PLS
            else:
                self.error_occurred.emit(f"Unsupported playlist file extension: {ext}")
                return None
        
        try:
            if format == PlaylistFormat.JSON:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    playlist = Playlist.from_dict(data)
            elif format == PlaylistFormat.M3U:
                playlist = self._load_from_m3u(file_path)
            elif format == PlaylistFormat.PLS:
                playlist = self._load_from_pls(file_path)
            else:
                self.error_occurred.emit(f"Unsupported playlist format: {format}")
                return None
            
            if not playlist:
                self.error_occurred.emit("Failed to parse playlist file")
                return None
            
            # Add the playlist to our collection
            self._playlists[playlist.uuid] = playlist
            
            # Set as current if we don't have one
            if not self._current_playlist_uuid:
                self._current_playlist_uuid = playlist.uuid
            
            self.playlist_loaded.emit(playlist.uuid)
            return playlist.uuid
            
        except Exception as e:
            self.error_occurred.emit(f"Error loading playlist: {str(e)}")
            return None
    
    def export_playlist(self, uuid: str, file_path: str, format: PlaylistFormat) -> bool:
        """
        Export a playlist to a different format.
        
        Args:
            uuid (str): UUID of the playlist
            file_path (str): Path where the playlist should be exported
            format (PlaylistFormat): Format to export the playlist to
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.save_playlist(uuid, file_path, format)
    
    def import_playlist(self, file_path: str, format: Optional[PlaylistFormat] = None) -> Optional[str]:
        """
        Import a playlist from a file.
        
        Args:
            file_path (str): Path to the playlist file
            format (Optional[PlaylistFormat]): Format of the playlist file, or None to auto-detect
            
        Returns:
            Optional[str]: UUID of the imported playlist, or None if importing failed
        """
        return self.load_playlist(file_path, format)
    
    def _save_as_m3u(self, playlist: Playlist, file_path: str) -> bool:
        """
        Save a playlist as an M3U file.
        
        Args:
            playlist (Playlist): The playlist to save
            file_path (str): Path where the playlist should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write M3U header
                f.write("#EXTM3U\n")
                
                # Write tracks
                for track in playlist.tracks:
                    # Write extended info if available
                    if 'duration' in track.metadata and 'artist' in track.metadata and 'title' in track.metadata:
                        duration_sec = track.metadata['duration'] // 1000  # Convert ms to seconds
                        title = track.metadata.get('title', os.path.basename(track.file_path))
                        f.write(f"#EXTINF:{duration_sec},{artist} - {title}\n")
                    
                    # Write track path (use absolute path to ensure compatibility)
                    f.write(f"{track.file_path}\n")
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error saving M3U playlist: {str(e)}")
            return False
    
    def _save_as_pls(self, playlist: Playlist, file_path: str) -> bool:
        """
        Save a playlist as a PLS file.
        
        Args:
            playlist (Playlist): The playlist to save
            file_path (str): Path where the playlist should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write PLS header
                f.write("[playlist]\n")
                f.write(f"NumberOfEntries={len(playlist.tracks)}\n")
                
                # Write tracks
                for i, track in enumerate(playlist.tracks, 1):
                    # Write track path
                    f.write(f"File{i}={track.file_path}\n")
                    
                    # Write track title if available
                    title = track.metadata.get('title', os.path.basename(track.file_path))
                    f.write(f"Title{i}={title}\n")
                    
                    # Write track length if available (in seconds)
                    length = track.metadata.get('duration', -1) // 1000 if track.metadata.get('duration') else -1
                    f.write(f"Length{i}={length}\n")
                
                # Write version
                f.write("Version=2\n")
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error saving PLS playlist: {str(e)}")
            return False
    
    def _load_from_m3u(self, file_path: str) -> Optional[Playlist]:
        """
        Load a playlist from an M3U file.
        
        Args:
            file_path (str): Path to the M3U file
            
        Returns:
            Optional[Playlist]: The loaded playlist, or None if loading failed
        """
        try:
            # Create a new playlist based on the file name
            playlist_name = os.path.splitext(os.path.basename(file_path))[0]
            playlist = Playlist(playlist_name)
            
            # Get the directory containing the playlist file for handling relative paths
            playlist_dir = os.path.dirname(os.path.abspath(file_path))
            
            # Parse the M3U file
            current_title = ""
            current_artist = ""
            current_duration = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#EXTM3U'):
                        # Skip empty lines and the M3U header
                        continue
                    
                    if line.startswith('#EXTINF:'):
                        # Parse extended info
                        # Format is typically: #EXTINF:123,Artist - Title
                        # or sometimes: #EXTINF:123,Title
                        info_part = line.split(':', 1)[1]
                        if ',' in info_part:
                            duration_str, title_part = info_part.split(',', 1)
                            try:
                                current_duration = int(float(duration_str)) * 1000  # Convert to ms
                            except ValueError:
                                current_duration = 0
                            
                            # Try to extract artist if present
                            if ' - ' in title_part:
                                current_artist, current_title = title_part.split(' - ', 1)
                            else:
                                current_title = title_part
                                current_artist = ""
                    
                    elif not line.startswith('#'):
                        # This is a track path
                        # Handle both absolute and relative paths
                        track_path = line
                        if not os.path.isabs(track_path):
                            # Convert relative path to absolute
                            track_path = os.path.join(playlist_dir, track_path)
                        
                        # Check if file exists
                        if os.path.exists(track_path):
                            # Create minimal metadata
                            metadata = {
                                'title': current_title or os.path.basename(track_path),
                                'artist': current_artist,
                                'duration': current_duration
                            }
                            
                            # Add track to playlist
                            track = Track(track_path, metadata)
                            playlist.add_track(track)
                            
                            # Reset for next track
                            current_title = ""
                            current_artist = ""
                            current_duration = 0
                        else:
                            self.error_occurred.emit(f"File not found: {track_path}")
            
            return playlist if playlist.tracks else None
            
        except Exception as e:
            self.error_occurred.emit(f"Error loading M3U playlist: {str(e)}")
            return None
    
    def _load_from_pls(self, file_path: str) -> Optional[Playlist]:
        """
        Load a playlist from a PLS file.
        
        Args:
            file_path (str): Path to the PLS file
            
        Returns:
            Optional[Playlist]: The loaded playlist, or None if loading failed
        """
        try:
            # Create a new playlist based on the file name
            playlist_name = os.path.splitext(os.path.basename(file_path))[0]
            playlist = Playlist(playlist_name)
            
            # Get the directory containing the playlist file for handling relative paths
            playlist_dir = os.path.dirname(os.path.abspath(file_path))
            
            # Parse the PLS file
            track_paths = {}  # Track number -> path
            track_titles = {}  # Track number -> title
            track_lengths = {}  # Track number -> length (duration in seconds)
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('[playlist]') or line.startswith('Version='):
                        # Skip empty lines, header and version
                        continue
                    
                    if line.startswith('NumberOfEntries='):
                        # Ignore this, we'll process all entries we find
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        
                        if key.startswith('File'):
                            try:
                                track_num = int(key[4:])
                                track_paths[track_num] = value
                            except ValueError:
                                continue
                        
                        elif key.startswith('Title'):
                            try:
                                track_num = int(key[5:])
                                track_titles[track_num] = value
                            except ValueError:
                                continue
                        
                        elif key.startswith('Length'):
                            try:
                                track_num = int(key[6:])
                                try:
                                    track_lengths[track_num] = int(value)
                                except ValueError:
                                    track_lengths[track_num] = -1
                            except ValueError:
                                continue
            
            # Now create tracks from the collected data
            for track_num in sorted(track_paths.keys()):
                track_path = track_paths[track_num]
                
                # Handle both absolute and relative paths
                if not os.path.isabs(track_path):
                    # Convert relative path to absolute
                    track_path = os.path.join(playlist_dir, track_path)
                
                # Check if file exists
                if os.path.exists(track_path):
                    # Create minimal metadata
                    metadata = {
                        'title': track_titles.get(track_num, os.path.basename(track_path)),
                        'duration': track_lengths.get(track_num, -1) * 1000 if track_lengths.get(track_num, -1) > 0 else None
                    }
                    
                    # Add track to playlist
                    track = Track(track_path, metadata)
                    playlist.add_track(track)
                else:
                    self.error_occurred.emit(f"File not found: {track_path}")
            
            return playlist if playlist.tracks else None
            
        except Exception as e:
            self.error_occurred.emit(f"Error loading PLS playlist: {str(e)}")
            return None
