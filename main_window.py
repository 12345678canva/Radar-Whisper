#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Main window module that implements the primary application interface
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from PyQt5.QtCore import (QDir, QFileInfo, QMimeData, QPoint, QSettings, QSize,
                          Qt, QTimer, QUrl, pyqtSlot)
from PyQt5.QtGui import (QCloseEvent, QDragEnterEvent, QDropEvent, QIcon,
                         QKeySequence, QPixmap, QResizeEvent)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import (QAction, QApplication, QDockWidget, QFileDialog,
                             QFrame, QHBoxLayout, QInputDialog, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QMenuBar, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSplitter,
                             QStatusBar, QStyle, QToolBar, QVBoxLayout,
                             QWidget)

from audio_player import AudioPlayer
from metadata_handler import MetadataHandler
from playlist_manager import PlaylistFormat, PlaylistManager, RepeatMode
from ui_components import (ColorScheme, MediaControls, PlaylistView, SearchBar,
                           Theme, TrackInfoPanel, TrackProgressBar,
                           VolumeSlider)


class MainWindow(QMainWindow):
    """
    Main application window for the Radar Whisper music player.
    Integrates all UI components and handles the application logic.
    """

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize components
        self._metadata_handler = MetadataHandler()
        self._audio_player = AudioPlayer()
        self._playlist_manager = PlaylistManager(self._metadata_handler)

        # Track whether we're closing the application
        self._is_closing = False

        # Set up theme
        self._theme = Theme.DARK

        # Initialize UI
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Load settings
        self._load_settings()

        # Set window properties
        self.setWindowTitle("Radar-Whisper")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setAcceptDrops(True)
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)

        # Create default playlist if no playlists exist
        if not self._playlist_manager.get_all_playlists():
            self._playlist_manager.create_playlist("Default Playlist")

        # Update UI
        self._update_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        # Set up central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create menu bar
        self._create_menu_bar()

        # Create main content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Playlist management
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(200)
        left_panel.setMaximumWidth(300)

        left_layout = QVBoxLayout(left_panel)

        # Playlist selector
        playlists_label = QLabel("Playlists")
        playlists_label.setProperty("title", True)

        self._playlists_list = QListWidget()
        self._playlists_list.setMinimumHeight(200)
        self._playlists_list.itemClicked.connect(self._on_playlist_selected)

        # Playlist controls
        playlist_controls_layout = QHBoxLayout()

        self._new_playlist_btn = QPushButton("+")
        self._new_playlist_btn.setToolTip("Create new playlist")
        self._new_playlist_btn.clicked.connect(self._on_new_playlist)

        self._remove_playlist_btn = QPushButton("-")
        self._remove_playlist_btn.setToolTip("Remove playlist")
        self._remove_playlist_btn.clicked.connect(self._on_remove_playlist)

        self._save_playlist_btn = QPushButton("💾")
        self._save_playlist_btn.setToolTip("Save playlist")
        self._save_playlist_btn.clicked.connect(self._on_save_playlist)

        self._load_playlist_btn = QPushButton("📂")
        self._load_playlist_btn.setToolTip("Load playlist")
        self._load_playlist_btn.clicked.connect(self._on_load_playlist)

        playlist_controls_layout.addWidget(self._new_playlist_btn)
        playlist_controls_layout.addWidget(self._remove_playlist_btn)
        playlist_controls_layout.addWidget(self._save_playlist_btn)
        playlist_controls_layout.addWidget(self._load_playlist_btn)

        # File browser (placeholder for now)
        files_label = QLabel("Library")
        files_label.setProperty("title", True)

        # Add to left layout
        left_layout.addWidget(playlists_label)
        left_layout.addWidget(self._playlists_list)
        left_layout.addLayout(playlist_controls_layout)
        left_layout.addWidget(files_label)
        left_layout.addStretch(1)

        # Center panel - Current playlist
        center_panel = QFrame()
        center_panel.setObjectName("centerPanel")

        center_layout = QVBoxLayout(center_panel)

        # Search bar
        self._search_bar = SearchBar()
        self._search_bar.search_text_changed.connect(self._on_search_text_changed)

        # Current playlist label
        self._current_playlist_label = QLabel("No Playlist Selected")
        self._current_playlist_label.setProperty("title", True)

        # Current playlist view
        self._playlist_view = PlaylistView()
        self._playlist_view.setMinimumHeight(200)
        self._playlist_view.track_double_clicked.connect(self._on_track_double_clicked)
        self._playlist_view.tracks_reordered.connect(self._on_tracks_reordered)

        # Add tracks button
        self._add_tracks_btn = QPushButton("Add Tracks")
        self._add_tracks_btn.clicked.connect(self._on_add_tracks)

        # Add to center layout
        center_layout.addWidget(self._search_bar)
        center_layout.addWidget(self._current_playlist_label)
        center_layout.addWidget(self._playlist_view)
        center_layout.addWidget(self._add_tracks_btn)

        # Right panel - Track info
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_panel.setMinimumWidth(250)
        right_panel.setMaximumWidth(350)

        right_layout = QVBoxLayout(right_panel)

        # Track info panel
        self._track_info_panel = TrackInfoPanel()

        # Add to right layout
        right_layout.addWidget(self._track_info_panel)

        # Add panels to splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(center_panel)
        content_splitter.addWidget(right_panel)

        # Set initial splitter sizes
        content_splitter.setSizes([200, 600, 300])

        # Bottom panel - Player controls
        bottom_panel = QFrame()
        bottom_panel.setObjectName("bottomPanel")
        bottom_panel.setMinimumHeight(120)
        bottom_panel.setMaximumHeight(150)

        bottom_layout = QVBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(10, 10, 10, 10)

        # Progress bar
        self._progress_bar = TrackProgressBar()
        self._progress_bar.seek_position.connect(self._on_seek_position)

        # Media controls
        self._media_controls = MediaControls()
        self._media_controls.pause_clicked.connect(self._on_pause)
        self._media_controls.stop_clicked.connect(self._on_stop)
        self._media_controls.next_clicked.connect(self._on_next_track)
        self._media_controls.previous_clicked.connect(self._on_previous_track)
        self._media_controls.shuffle_toggled.connect(self._on_shuffle_toggled)
        self._media_controls.repeat_mode_changed.connect(self._on_repeat_mode_changed)

        # Volume slider
        self._volume_slider = VolumeSlider()
        self._volume_slider.volume_changed.connect(self._on_volume_changed)
        self._volume_slider.mute_toggled.connect(self._on_mute_toggled)

        # Control row layout
        control_row = QHBoxLayout()
        control_row.addWidget(self._media_controls, 1)  # Stretch to fill space
        control_row.addWidget(self._volume_slider)

        # Add to bottom layout
        bottom_layout.addWidget(self._progress_bar)
        bottom_layout.addLayout(control_row)

        # Add components to main layout
        main_layout.addWidget(content_splitter, 1)  # Stretch to fill space
        main_layout.addWidget(bottom_panel)

        # Create status bar
        self._status_bar = self.statusBar()
        self._status_bar.showMessage("Ready")

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        # Main menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Open file action
        open_action = QAction("&Open Files...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._on_open_files)
        file_menu.addAction(open_action)

        # Open folder action
        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        # New playlist action
        new_playlist_action = QAction("&New Playlist", self)
        new_playlist_action.setShortcut("Ctrl+N")
        new_playlist_action.triggered.connect(self._on_new_playlist)
        file_menu.addAction(new_playlist_action)

        # Load playlist action
        load_playlist_action = QAction("&Load Playlist...", self)
        load_playlist_action.setShortcut("Ctrl+L")
        load_playlist_action.triggered.connect(self._on_load_playlist)
        file_menu.addAction(load_playlist_action)

        # Save playlist action
        save_playlist_action = QAction("&Save Playlist...", self)
        save_playlist_action.setShortcut("Ctrl+S")
        save_playlist_action.triggered.connect(self._on_save_playlist)
        file_menu.addAction(save_playlist_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Playback menu
        playback_menu = menu_bar.addMenu("&Playback")

        # Play/Pause action
        self._play_pause_action = QAction("&Play", self)
        self._play_pause_action.setShortcut("Space")
        self._play_pause_action.triggered.connect(self._toggle_play_pause)
        playback_menu.addAction(self._play_pause_action)

        # Stop action
        stop_action = QAction("&Stop", self)
        stop_action.setShortcut("Ctrl+.")
        stop_action.triggered.connect(self._on_stop)
        playback_menu.addAction(stop_action)

        playback_menu.addSeparator()

        # Next track action
        next_action = QAction("&Next Track", self)
        next_action.setShortcut("Ctrl+Right")
        next_action.triggered.connect(self._on_next_track)
        playback_menu.addAction(next_action)

        # Previous track action
        prev_action = QAction("&Previous Track", self)
        prev_action.setShortcut("Ctrl+Left")
        prev_action.triggered.connect(self._on_previous_track)
        playback_menu.addAction(prev_action)

        playback_menu.addSeparator()

        # Toggle shuffle action
        self._shuffle_action = QAction("&Shuffle", self)
        self._shuffle_action.setShortcut("Ctrl+H")
        self._shuffle_action.setCheckable(True)
        self._shuffle_action.triggered.connect(lambda checked: self._on_shuffle_toggled(checked))
        playback_menu.addAction(self._shuffle_action)

        # Repeat submenu
        repeat_menu = playback_menu.addMenu("&Repeat")

        # No repeat action
        self._no_repeat_action = QAction("&No Repeat", self)
        self._no_repeat_action.setCheckable(True)
        self._no_repeat_action.setChecked(True)
        self._no_repeat_action.triggered.connect(lambda: self._on_repeat_mode_changed(0))
        repeat_menu.addAction(self._no_repeat_action)

        # Repeat playlist action
        self._repeat_playlist_action = QAction("Repeat &Playlist", self)
        self._repeat_playlist_action.setCheckable(True)
        self._repeat_playlist_action.triggered.connect(lambda: self._on_repeat_mode_changed(1))
        repeat_menu.addAction(self._repeat_playlist_action)

        # Repeat track action
        self._repeat_track_action = QAction("Repeat &Track", self)
        self._repeat_track_action.setCheckable(True)
        self._repeat_track_action.triggered.connect(lambda: self._on_repeat_mode_changed(2))
        repeat_menu.addAction(self._repeat_track_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")

        # Dark theme action
        self._dark_theme_action = QAction("&Dark Theme", self)
        self._dark_theme_action.setCheckable(True)
        self._dark_theme_action.setChecked(self._theme == Theme.DARK)
        self._dark_theme_action.triggered.connect(lambda: self._set_theme(Theme.DARK))
        theme_menu.addAction(self._dark_theme_action)

        # Light theme action
        self._light_theme_action = QAction("&Light Theme", self)
        self._light_theme_action.setCheckable(True)
        self._light_theme_action.setChecked(self._theme == Theme.LIGHT)
        self._light_theme_action.triggered.connect(lambda: self._set_theme(Theme.LIGHT))
        theme_menu.addAction(self._light_theme_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("&About Radar Whisper", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Connect audio player signals
        self._audio_player.playback_state_changed.connect(self._on_playback_state_changed)
        self._audio_player.position_changed.connect(self._on_position_changed)
        self._audio_player.duration_changed.connect(self._on_duration_changed)
        self._audio_player.metadata_changed.connect(self._on_metadata_changed)
        self._audio_player.error_occurred.connect(self._on_audio_error)

        # Connect playlist manager signals
        self._playlist_manager.playlist_changed.connect(self._on_playlist_changed)
        self._playlist_manager.playlist_loaded.connect(self._on_playlist_loaded)
        self._playlist_manager.current_track_changed.connect(self._on_current_track_changed)
        self._playlist_manager.error_occurred.connect(self._on_playlist_error)

    def _load_settings(self) -> None:
        """Load application settings."""
        settings = QSettings("RadarWhisper", "RadarWhisper")

        # Restore window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Restore window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)

        # Restore theme
        theme_str = settings.value("theme", "dark")
        self._theme = Theme.DARK if theme_str.lower() == "dark" else Theme.LIGHT

        # Restore volume
        volume = settings.value("volume", 100, type=int)
        self._volume_slider.set_volume(volume)

        # Restore mute state
        muted = settings.value("muted", False, type=bool)
        self._volume_slider.set_muted(muted)

        # Restore shuffle state
        shuffle = settings.value("shuffle", False, type=bool)
        self._media_controls.set_shuffle_state(shuffle)
        self._playlist_manager.set_shuffle_mode(shuffle)

        # Restore repeat mode
        repeat_mode = settings.value("repeatMode", 0)
        self._media_controls.set_repeat_mode(repeat_mode)

        # Apply theme
        self._set_theme(self._theme)

    def _save_settings(self) -> None:
        """Save application settings."""
        settings = QSettings("RadarWhisper", "RadarWhisper")

        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())

        # Save window state
        settings.setValue("windowState", self.saveState())

        # Save theme
        settings.setValue("theme", "dark" if self._theme == Theme.DARK else "light")

        # Save volume
        settings.setValue("volume", self._volume_slider.get_volume())

        # Save mute state
        settings.setValue("muted", self._volume_slider.is_muted())

        # Save shuffle state
        settings.setValue("shuffle", self._playlist_manager._shuffle_mode)

        # Save repeat mode
        settings.setValue("repeatMode", self._playlist_manager._repeat_mode)

    def _update_ui(self) -> None:
        """Update the UI to reflect the current state."""
        # Update playlists list
        self._update_playlists_list()

        # Update current playlist display
        self._update_current_playlist()

        # Update theme
        self._update_theme()

    def _update_theme(self) -> None:
        """Update the UI with the current theme."""
        # Set theme for components
        self._progress_bar.set_theme(self._theme)
        self._volume_slider.set_theme(self._theme)
        self._media_controls.set_theme(self._theme)
        self._playlist_view.set_theme(self._theme)
        self._track_info_panel.set_theme(self._theme)
        self._search_bar.set_theme(self._theme)

        # Set application stylesheet
        self.setStyleSheet(ColorScheme.get_stylesheet(self._theme))

        # Update menu actions
        self._dark_theme_action.setChecked(self._theme == Theme.DARK)
        self._light_theme_action.setChecked(self._theme == Theme.LIGHT)

    def _set_theme(self, theme: Theme) -> None:
        """
        Set the application theme.

        Args:
            theme (Theme): The theme to set
        """
        if self._theme != theme:
            self._theme = theme
            self._update_theme()

    def _update_playlists_list(self) -> None:
        """Update the playlists list with current playlists."""
        # Clear the list
        self._playlists_list.clear()

        # Add all playlists
        playlists = self._playlist_manager.get_all_playlists()
        for playlist in playlists:
            item = QListWidgetItem(playlist.name)
            item.setData(Qt.UserRole, playlist.uuid)
            self._playlists_list.addItem(item)

        # Select the current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if current_playlist:
            for i in range(self._playlists_list.count()):
                item = self._playlists_list.item(i)
                if item.data(Qt.UserRole) == current_playlist.uuid:
                    self._playlists_list.setCurrentItem(item)
                    break

    def _update_current_playlist(self) -> None:
        """Update the current playlist display."""
        # Clear the playlist view
        self._playlist_view.clear()

        # Get the current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            self._current_playlist_label.setText("No Playlist Selected")
            return

        # Update the playlist label
        self._current_playlist_label.setText(current_playlist.name)

        # Add tracks to the playlist view
        for track in current_playlist.tracks:
            title = track.metadata.get('title', os.path.basename(track.file_path))
            artist = track.metadata.get('artist', 'Unknown Artist')
            duration = track.metadata.get('duration_str', '')

            # Get album art if available
            album_art = None
            if 'album_art' in track.metadata:
                album_art = QPixmap(track.metadata['album_art'])

            # Add to playlist view
            self._playlist_view.add_track(title, artist, duration, album_art)

    def _on_playlist_selected(self, item: QListWidgetItem) -> None:
        """
        Handle playlist selection.

        Args:
            item (QListWidgetItem): The selected playlist item
        """
        playlist_uuid = item.data(Qt.UserRole)
        if playlist_uuid:
            self._playlist_manager.set_current_playlist(playlist_uuid)
            self._update_current_playlist()

    def _on_new_playlist(self) -> None:
        """Create a new playlist."""
        # Show dialog to get playlist name
        name, ok = QInputDialog.getText(
            self, "New Playlist", "Enter playlist name:",
            QLineEdit.Normal, "New Playlist"
        )

        if ok and name:
            # Create the playlist
            playlist_uuid = self._playlist_manager.create_playlist(name)

            # Update the UI
            self._update_playlists_list()

            # Select the new playlist
            for i in range(self._playlists_list.count()):
                item = self._playlists_list.item(i)
                if item.data(Qt.UserRole) == playlist_uuid:
                    self._playlists_list.setCurrentItem(item)
                    break

    def _on_remove_playlist(self) -> None:
        """Remove the selected playlist."""
        # Get the selected playlist
        selected_items = self._playlists_list.selectedItems()
        if not selected_items:
            return

        playlist_uuid = selected_items[0].data(Qt.UserRole)
        playlist = self._playlist_manager.get_playlist(playlist_uuid)

        if not playlist:
            return

        # Confirm deletion
        result = QMessageBox.question(
            self, "Remove Playlist",
            f"Are you sure you want to remove the playlist '{playlist.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if result == QMessageBox.Yes:
            # Remove the playlist
            self._playlist_manager.delete_playlist(playlist_uuid)

            # Update the UI
            self._update_playlists_list()
            self._update_current_playlist()

    def _on_save_playlist(self) -> None:
        """Save the current playlist to a file."""
        # Get the current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            QMessageBox.warning(
                self, "No Playlist",
                "No playlist is selected to save."
            )
            return

        # Show save dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Playlist",
            os.path.join(QDir.homePath(), f"{current_playlist.name}.json"),
            "JSON Playlist (*.json);;M3U Playlist (*.m3u);;PLS Playlist (*.pls)"
        )

        if not file_path:
            return

        # Determine format from selected filter
        format = PlaylistFormat.JSON
        if selected_filter == "M3U Playlist (*.m3u)":
            format = PlaylistFormat.M3U
        elif selected_filter == "PLS Playlist (*.pls)":
            format = PlaylistFormat.PLS

        # Save the playlist
        success = self._playlist_manager.save_playlist(current_playlist.uuid, file_path, format)

        if success:
            self._status_bar.showMessage(f"Playlist saved to {file_path}", 3000)
        else:
            QMessageBox.warning(
                self, "Save Failed",
                "Failed to save the playlist. Please try again."
            )

    def _on_load_playlist(self) -> None:
        """Load a playlist from a file."""
        # Show open dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Playlist", QDir.homePath(),
            "All Playlists (*.json *.m3u *.m3u8 *.pls);;JSON Playlist (*.json);;M3U Playlist (*.m3u *.m3u8);;PLS Playlist (*.pls)"
        )

        if not file_path:
            return

        # Load the playlist
        playlist_uuid = self._playlist_manager.load_playlist(file_path)

        if playlist_uuid:
            self._status_bar.showMessage(f"Playlist loaded from {file_path}", 3000)
            self._update_playlists_list()

            # Select the loaded playlist
            for i in range(self._playlists_list.count()):
                item = self._playlists_list.item(i)
                if item.data(Qt.UserRole) == playlist_uuid:
                    self._playlists_list.setCurrentItem(item)
                    break
        else:
            QMessageBox.warning(
                self, "Load Failed",
                "Failed to load the playlist. Please try again."
            )

    def _on_open_files(self) -> None:
        """Open audio files and add them to the current playlist."""
        # Show open dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Open Audio Files", QDir.homePath(),
            "Audio Files (*.mp3 *.flac *.wav *.m4a *.ogg);;All Files (*.*)"
        )

        if not file_paths:
            return

        # Ensure we have a current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            # Create a new playlist if none exists
            playlist_uuid = self._playlist_manager.create_playlist("New Playlist")
            self._update_playlists_list()
        else:
            playlist_uuid = current_playlist.uuid

        # Add tracks to the playlist
        count = self._playlist_manager.add_tracks_to_playlist(playlist_uuid, file_paths)

        # Update the UI
        self._update_current_playlist()

        # Show status message
        self._status_bar.showMessage(f"Added {count} tracks to playlist", 3000)

    def _on_open_folder(self) -> None:
        """Open a folder and add all audio files to the current playlist."""
        # Show folder dialog
        folder_path = QFileDialog.getExistingDirectory(
            self, "Open Folder", QDir.homePath(),
            QFileDialog.ShowDirsOnly
        )

        if not folder_path:
            return

        # Collect audio files from the folder
        audio_extensions = ['.mp3', '.flac', '.wav', '.m4a', '.ogg']
        file_paths = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    file_paths.append(os.path.join(root, file))

        if not file_paths:
            self._status_bar.showMessage("No audio files found in the selected folder", 3000)
            return

        # Ensure we have a current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            # Create a new playlist named after the folder
            folder_name = os.path.basename(folder_path)
            playlist_uuid = self._playlist_manager.create_playlist(folder_name)
            self._update_playlists_list()
        else:
            playlist_uuid = current_playlist.uuid

        # Add tracks to the playlist
        count = self._playlist_manager.add_tracks_to_playlist(playlist_uuid, file_paths)

        # Update the UI
        self._update_current_playlist()

        # Show status message
        self._status_bar.showMessage(f"Added {count} tracks from {folder_path}", 3000)

    def _on_add_tracks(self) -> None:
        """Add tracks to the current playlist."""
        # Make sure we have a current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            QMessageBox.warning(
                self, "No Playlist",
                "Please create or select a playlist first."
            )
            return

        # Show open dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Audio Files", QDir.homePath(),
            "Audio Files (*.mp3 *.flac *.wav *.m4a *.ogg);;All Files (*.*)"
        )

        if not file_paths:
            return

        # Add tracks to the playlist
        count = self._playlist_manager.add_tracks_to_playlist(current_playlist.uuid, file_paths)

        # Update the UI
        self._update_current_playlist()

        # Show status message
        self._status_bar.showMessage(f"Added {count} tracks to playlist", 3000)

        """Handle play command."""
        # Get the current track
        current_track = self._playlist_manager.get_current_track()
        if not current_track:
            # Try to play the first track if none is selected
            next_track = self._playlist_manager.get_next_track()
            if not next_track:
                self._status_bar.showMessage("No tracks to play", 3000)
                return
            current_track = next_track

        # Start playback of the current track
        track, _ = current_track
        self._audio_player.load_file(track.file_path)
        self._audio_player.play()

        # Update UI
        self._media_controls.set_playing_state(True)
        self._update_status(f"Now playing: {track.metadata.get('title', os.path.basename(track.file_path))}")

    def _on_pause(self) -> None:
        """Handle pause command."""
        if self._audio_player.is_playing():
            self._audio_player.pause()
            self._media_controls.set_playing_state(False)
            self._update_status("Paused")

    def _on_stop(self) -> None:
        """Handle stop command."""
        self._audio_player.stop()
        self._media_controls.set_playing_state(False)
        self._progress_bar.set_position(0)
        self._update_status("Stopped")

    def _toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""
        if self._audio_player.is_playing():
            self._on_pause()
        else:
            self._on_play()

    def _on_next_track(self) -> None:
        """Play the next track in the playlist."""
        next_track = self._playlist_manager.get_next_track()
        if next_track:
            track, index = next_track
            self._audio_player.load_file(track.file_path)
            self._audio_player.play()
            self._media_controls.set_playing_state(True)
            self._update_status(f"Now playing: {track.metadata.get('title', os.path.basename(track.file_path))}")
        else:
            self._update_status("No next track available")

    def _on_previous_track(self) -> None:
        """Play the previous track in the playlist."""
        prev_track = self._playlist_manager.get_previous_track()
        if prev_track:
            track, index = prev_track
            self._audio_player.load_file(track.file_path)
            self._audio_player.play()
            self._media_controls.set_playing_state(True)
            self._update_status(f"Now playing: {track.metadata.get('title', os.path.basename(track.file_path))}")
        else:
            self._update_status("No previous track available")

    def _on_seek_position(self, position: int) -> None:
        """
        Handle seeking to a new position in the track.

        Args:
            position (int): New position in milliseconds
        """
        self._audio_player.set_position(position)

    def _on_volume_changed(self, volume: int) -> None:
        """
        Handle volume changes.

        Args:
            volume (int): New volume level (0-100)
        """
        self._audio_player.set_volume(volume)

    def _on_mute_toggled(self, muted: bool) -> None:
        """
        Handle mute toggling.

        Args:
            muted (bool): True if muted, False otherwise
        """
        if muted:
            # Store current volume before muting
            self._audio_player.set_volume(0)
        else:
            # Restore volume
            self._audio_player.set_volume(self._volume_slider.get_volume())

    def _on_shuffle_toggled(self, enabled: bool) -> None:
        """
        Handle shuffle mode toggling.

        Args:
            enabled (bool): True to enable shuffle mode, False to disable
        """
        self._playlist_manager.set_shuffle_mode(enabled)
        self._shuffle_action.setChecked(enabled)
        self._update_status(f"Shuffle {'enabled' if enabled else 'disabled'}")

    def _on_repeat_mode_changed(self, mode: int) -> None:
        """
        Handle repeat mode changes.

        Args:
            mode (int): Repeat mode (0=No repeat, 1=Repeat playlist, 2=Repeat track)
        """
        # Update playlist manager
        repeat_mode = RepeatMode(mode + 1)  # Convert to RepeatMode enum
        self._playlist_manager.set_repeat_mode(mode)

        # Update menu actions
        self._no_repeat_action.setChecked(mode == 0)
        self._repeat_playlist_action.setChecked(mode == 1)
        self._repeat_track_action.setChecked(mode == 2)

        # Update UI
        self._media_controls.set_repeat_mode(mode)

        # Update status
        mode_text = ["No repeat", "Repeat playlist", "Repeat track"][mode]
        self._update_status(f"Repeat mode: {mode_text}")

    def _on_playback_state_changed(self, state: int) -> None:
        """
        Handle playback state changes from the audio player.

        Args:
            state (int): New playback state
        """
        # QMediaPlayer.StoppedState = 0, PlayingState = 1, PausedState = 2
        if state == 1:  # Playing
            self._media_controls.set_playing_state(True)
            self._play_pause_action.setText("&Pause")
        else:
            self._media_controls.set_playing_state(False)
            self._play_pause_action.setText("&Play")

            # If we're stopped and not at the end, go to the next track
            if state == 0 and self._audio_player.get_position() >= self._audio_player.get_duration() - 500:
                # Small delay to allow the UI to update
                QTimer.singleShot(100, self._on_next_track)

    def _on_position_changed(self, position: int) -> None:
        """
        Handle position changes from the audio player.

        Args:
            position (int): New position in milliseconds
        """
        self._progress_bar.set_position(position)

    def _on_duration_changed(self, duration: int) -> None:
        """
        Handle duration changes from the audio player.

        Args:
            duration (int): New duration in milliseconds
        """
        self._progress_bar.set_duration(duration)

    def _on_metadata_changed(self, metadata: Dict[str, Any]) -> None:
        """
        Handle metadata changes from the audio player.

        Args:
            metadata (Dict[str, Any]): New track metadata
        """
        # Update track info display
        self._track_info_panel.update_track_info(metadata)

        # Update window title
        title = metadata.get('title', 'Unknown')
        artist = metadata.get('artist', 'Unknown')
        self.setWindowTitle(f"{title} - {artist} | Radar Whisper")

    def _on_audio_error(self, error_msg: str) -> None:
        """
        Handle errors from the audio player.

        Args:
            error_msg (str): Error message
        """
        self._show_error_message("Audio Player Error", error_msg)

        # Try to recover by moving to the next track
        self._on_next_track()

    def _on_playlist_error(self, error_msg: str) -> None:
        """
        Handle errors from the playlist manager.

        Args:
            error_msg (str): Error message
        """
        self._show_error_message("Playlist Error", error_msg)

    def _on_playlist_changed(self, uuid: str) -> None:
        """
        Handle playlist changes.

        Args:
            uuid (str): UUID of the changed playlist
        """
        # Update the UI if this is the current playlist
        current_playlist = self._playlist_manager.get_current_playlist()
        if current_playlist and current_playlist.uuid == uuid:
            self._update_current_playlist()

    def _on_playlist_loaded(self, uuid: str) -> None:
        """
        Handle playlist loaded event.

        Args:
            uuid (str): UUID of the loaded playlist
        """
        # Update the UI
        self._update_playlists_list()
        self._update_current_playlist()

    def _on_current_track_changed(self, index: int) -> None:
        """
        Handle current track changes.

        Args:
            index (int): Index of the new current track
        """
        # Update UI to highlight the current track
        self._playlist_view.setCurrentRow(index)

        # If we're playing, load and play the new track
        if self._audio_player.is_playing():
            current_track = self._playlist_manager.get_current_track()
            if current_track:
                track, _ = current_track
                self._audio_player.load_file(track.file_path)
                self._audio_player.play()

    def _on_track_double_clicked(self, index: int) -> None:
        """
        Handle a track being double-clicked in the playlist view.

        Args:
            index (int): Index of the clicked track
        """
        # Set as current track and play it
        current_playlist = self._playlist_manager.get_current_playlist()
        if current_playlist and 0 <= index < len(current_playlist.tracks):
            # Set as current track
            self._playlist_manager.set_current_track(index)

            # Play the track
            track = current_playlist.tracks[index]
            self._audio_player.load_file(track.file_path)
            self._audio_player.play()
            self._media_controls.set_playing_state(True)

    def _on_tracks_reordered(self, from_index: int, to_index: int) -> None:
        """
        Handle tracks being reordered in the playlist.

        Args:
            from_index (int): Original index of the track
            to_index (int): New index of the track
        """
        # Update the playlist in the manager
        current_playlist = self._playlist_manager.get_current_playlist()
        if not current_playlist:
            return

        # Move the track in the playlist
        current_playlist.move_track(from_index, to_index)

        # If this is the current track, update the current track index
        current_track = self._playlist_manager.get_current_track()
        if current_track:
            _, current_index = current_track
            if current_index == from_index:
                self._playlist_manager.set_current_track(to_index)

        # Update the UI
        self._update_current_playlist()

    def _on_search_text_changed(self, text: str) -> None:
        """
        Handle search text changes.

        Args:
            text (str): New search text
        """
        # Filter the playlist view
        if not text:
            # Show all items
            for i in range(self._playlist_view.count()):
                self._playlist_view.item(i).setHidden(False)
        else:
            # Filter items based on the search text
            for i in range(self._playlist_view.count()):
                item = self._playlist_view.item(i)
                item_text = item.text().lower()
                item.setHidden(text.lower() not in item_text)

    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self, "About Radar-Whisper",
            "<h1>Radar-Whisper</h1>"
            "<p>This is a music player designed to play full playlists and albums. The project is still a work in progress, so several features are incomplete or may contain bugs.</p>"
            "<p>Version 0.9.0</p>"
            "<p>2025 Ivan-Ayub97</p>"
        )

    def _show_error_message(self, title: str, message: str) -> None:
        """
        Show an error message dialog.

        Args:
            title (str): Dialog title
            message (str): Error message
        """
        QMessageBox.critical(self, title, message)

    def _update_status(self, message: str) -> None:
        """
        Update the status bar with a message.

        Args:
            message (str): Status message to display
        """
        self._status_bar.showMessage(message, 3000)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Args:
            event (QCloseEvent): Close event
        """
        # Prevent multiple closings
        if self._is_closing:
            event.accept()
            return

        self._is_closing = True

        # Stop playback
        self._audio_player.stop()

        # Save settings
        self._save_settings()

        # Accept the event
        event.accept()
