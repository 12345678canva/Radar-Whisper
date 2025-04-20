#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Audio player module for handling playback functionality
"""

from typing import Optional, Callable, List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class AudioPlayer(QObject):
    """
    Handles audio playback functionality for the Radar Whisper application.
    Uses QMediaPlayer to manage audio playback, volume control, and seeking.
    """

    # Define signals for communication with UI
    playback_state_changed = pyqtSignal(int)  # QMediaPlayer::State
    position_changed = pyqtSignal(int)  # Position in milliseconds
    duration_changed = pyqtSignal(int)  # Duration in milliseconds
    metadata_changed = pyqtSignal(dict)  # Dictionary of metadata
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Initialize the audio player with a QMediaPlayer instance.

        Args:
            parent (Optional[QObject]): Parent QObject, if any
        """
        super().__init__(parent)

        self._player = QMediaPlayer()
        self._current_track_path: Optional[str] = None
        self._current_track_metadata: Dict[str, Any] = {}

        # Connect internal signals
        self._player.stateChanged.connect(self.playback_state_changed.emit)
        self._player.positionChanged.connect(self.position_changed.emit)
        self._player.durationChanged.connect(self.duration_changed.emit)
        self._player.error.connect(self._handle_error)
        self._player.mediaStatusChanged.connect(self._handle_media_status)

    @pyqtSlot(str)
    def load_file(self, file_path: str) -> bool:
        """
        Load an audio file into the player.

        Args:
            file_path (str): Path to the audio file

        Returns:
            bool: True if the file was loaded successfully, False otherwise
        """
        if not file_path:
            return False

        url = QUrl.fromLocalFile(file_path)
        media_content = QMediaContent(url)
        self._player.setMedia(media_content)
        self._current_track_path = file_path

        # Metadata will be populated when the media is loaded
        return True

    @pyqtSlot()
    def play(self) -> None:
        """Start or resume playback."""
        self._player.play()

    @pyqtSlot()
    def pause(self) -> None:
        """Pause playback."""
        self._player.pause()

    @pyqtSlot()
    def stop(self) -> None:
        """Stop playback."""
        self._player.stop()

    @pyqtSlot(int)
    def set_position(self, position: int) -> None:
        """
        Set the playback position.

        Args:
            position (int): Position in milliseconds
        """
        self._player.setPosition(position)

    @pyqtSlot(int)
    def set_volume(self, volume: int) -> None:
        """
        Set the playback volume.

        Args:
            volume (int): Volume level (0-100)
        """
        self._player.setVolume(volume)

    def get_position(self) -> int:
        """
        Get the current playback position.

        Returns:
            int: Current position in milliseconds
        """
        return self._player.position()

    def get_duration(self) -> int:
        """
        Get the duration of the current track.

        Returns:
            int: Duration in milliseconds
        """
        return self._player.duration()

    def get_volume(self) -> int:
        """
        Get the current volume level.

        Returns:
            int: Volume level (0-100)
        """
        return self._player.volume()

    def is_playing(self) -> bool:
        """
        Check if the player is currently playing.

        Returns:
            bool: True if playing, False otherwise
        """
        return self._player.state() == QMediaPlayer.PlayingState

    def is_paused(self) -> bool:
        """
        Check if the player is currently paused.

        Returns:
            bool: True if paused, False otherwise
        """
        return self._player.state() == QMediaPlayer.PausedState

    def get_current_track_path(self) -> Optional[str]:
        """
        Get the path of the currently loaded track.

        Returns:
            Optional[str]: Path to the current track, or None if no track is loaded
        """
        return self._current_track_path

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get the metadata of the currently loaded track.

        Returns:
            Dict[str, Any]: Dictionary containing track metadata
        """
        return self._current_track_metadata

    def toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""
        if self.is_playing():
            self.pause()
        else:
            self.play()

    @pyqtSlot(QMediaPlayer.Error)
    def _handle_error(self, error: QMediaPlayer.Error) -> None:
        """
        Handle errors from the media player.

        Args:
            error (QMediaPlayer.Error): Error code from QMediaPlayer
        """
        error_msg = "Unknown error"

        if error == QMediaPlayer.ResourceError:
            error_msg = "Resource error: Could not access the media"
        elif error == QMediaPlayer.FormatError:
            error_msg = "Format error: Unsupported media format"
        elif error == QMediaPlayer.NetworkError:
            error_msg = "Network error: Problem with network access"
        elif error == QMediaPlayer.AccessDeniedError:
            error_msg = "Access denied error: Permission denied"
        elif error == QMediaPlayer.ServiceMissingError:
            error_msg = "Service missing error: Media service not available"

        # Append the error string from the player if available
        if self._player.errorString():
            error_msg += f" ({self._player.errorString()})"

        self.error_occurred.emit(error_msg)

    @pyqtSlot(QMediaPlayer.MediaStatus)
    def _handle_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        """
        Handle media status changes.

        Args:
            status (QMediaPlayer.MediaStatus): Current media status
        """
        if status == QMediaPlayer.LoadedMedia:
            # When media is loaded, extract and update metadata
            self._update_metadata()
        elif status == QMediaPlayer.EndOfMedia:
            # When we reach the end of the media, emit a signal that can be used
            # to automatically play the next track
            self.position_changed.emit(self.get_duration())

    def _update_metadata(self) -> None:
        """Extract and update metadata from the current media."""
        if not self._current_track_path:
            return

        # Clear previous metadata
        self._current_track_metadata = {}

        # Get metadata from QMediaPlayer
        metadata = {}

        # Get basic metadata that QMediaPlayer provides
        title = self._player.metaData("Title")
        if title:
            metadata["title"] = title

        artist = self._player.metaData("ContributingArtist") or self._player.metaData("AlbumArtist")
        if artist:
            metadata["artist"] = artist

        album = self._player.metaData("AlbumTitle")
        if album:
            metadata["album"] = album

        year = self._player.metaData("Year")
        if year:
            metadata["year"] = year

        genre = self._player.metaData("Genre")
        if genre:
            metadata["genre"] = genre

        # If no metadata was found or it's incomplete, try to extract some from the filename
        if not metadata.get("title"):
            import os
            filename = os.path.basename(self._current_track_path)
            name, _ = os.path.splitext(filename)
            metadata["title"] = name

        # Store the metadata
        self._current_track_metadata = metadata

        # Emit the signal with the metadata
        self.metadata_changed.emit(self._current_track_metadata)
