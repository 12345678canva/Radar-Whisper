#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
UI components module with custom styled widgets
"""

import os
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import (QByteArray, QDataStream, QEvent, QIODevice,
                          QMimeData, QModelIndex, QObject, QPoint, QRect,
                          QSize, Qt, pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QCursor, QDrag, QDragEnterEvent,
                         QDropEvent, QFont, QFontMetrics, QIcon,
                         QLinearGradient, QMouseEvent, QPainter, QPaintEvent,
                         QPalette, QPen, QPixmap, QResizeEvent)
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QFileDialog, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem, QMenu,
                             QPushButton, QScrollArea, QSizePolicy, QSlider,
                             QStyle, QStyledItemDelegate, QStyleOption,
                             QStyleOptionViewItem, QToolButton, QVBoxLayout,
                             QWidget)


class Theme(Enum):
    """Enumeration for application themes."""
    DARK = auto()
    LIGHT = auto()

class RepeatMode(Enum):
    NONE = 0
    PLAYLIST = 1
    TRACK = 2

class ColorScheme:
    """
    Defines color schemes for light and dark themes.
    """

    # Dark theme colors
    DARK = {
        'background': '#121212',
        'secondary_background': '#1e1e1e',
        'surface': '#272727',
        'primary': '#bb86fc',
        'secondary': '#03dac6',
        'on_background': '#ffffff',
        'on_surface': '#dddddd',
        'on_primary': '#000000',
        'on_secondary': '#000000',
        'hover': '#3a3a3a',
        'pressed': '#4a4a4a',
        'slider_track': '#3a3a3a',
        'slider_handle': '#bb86fc',
        'progress_bar': '#bb86fc',
        'progress_bar_background': '#3a3a3a',
        'border': '#333333',
        'error': '#cf6679',
    }

    # Light theme colors
    LIGHT = {
        'background': '#f5f5f5',
        'secondary_background': '#e5e5e5',
        'surface': '#ffffff',
        'primary': '#6200ee',
        'secondary': '#03dac6',
        'on_background': '#000000',
        'on_surface': '#333333',
        'on_primary': '#ffffff',
        'on_secondary': '#000000',
        'hover': '#e0e0e0',
        'pressed': '#d0d0d0',
        'slider_track': '#c0c0c0',
        'slider_handle': '#6200ee',
        'progress_bar': '#6200ee',
        'progress_bar_background': '#c0c0c0',
        'border': '#cccccc',
        'error': '#b00020',
    }

    @staticmethod
    def get_color(theme: Theme, color_name: str) -> str:
        """
        Get a color value from the current theme.

        Args:
            theme (Theme): The current theme
            color_name (str): Name of the color to retrieve

        Returns:
            str: Hex color value
        """
        if theme == Theme.DARK:
            return ColorScheme.DARK.get(color_name, '#ffffff')
        else:
            return ColorScheme.LIGHT.get(color_name, '#000000')

    @staticmethod
    def get_stylesheet(theme: Theme) -> str:
        """
        Get the full stylesheet for the specified theme.

        Args:
            theme (Theme): The theme to generate a stylesheet for

        Returns:
            str: CSS stylesheet
        """
        if theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            /* Global Styles */
            QWidget {{
                background-color: {colors['background']};
                color: {colors['on_background']};
                font-family: "Segoe UI", "Arial", sans-serif;
            }}

            /* Buttons */
            QPushButton {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}

            QPushButton:hover {{
                background-color: {colors['hover']};
            }}

            QPushButton:pressed {{
                background-color: {colors['pressed']};
            }}

            QPushButton:disabled {{
                background-color: {colors['surface']};
                color: rgba({colors['on_surface']}, 0.38);
            }}

            /* Primary Button */
            QPushButton[primary="true"] {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
            }}

            QPushButton[primary="true"]:hover {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
            }}

            /* Sliders */
            QSlider::groove:horizontal {{
                height: 4px;
                background: {colors['slider_track']};
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                background: {colors['slider_handle']};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {colors['primary']};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}

            /* Progress Bar */
            QProgressBar {{
                border: none;
                background-color: {colors['progress_bar_background']};
                height: 4px;
                border-radius: 2px;
            }}

            QProgressBar::chunk {{
                background-color: {colors['progress_bar']};
                border-radius: 2px;
            }}

            /* Labels */
            QLabel {{
                color: {colors['on_background']};
            }}

            QLabel[title="true"] {{
                font-size: 18px;
                font-weight: bold;
            }}

            /* Line Edits */
            QLineEdit {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
            }}

            QLineEdit:focus {{
                border: 1px solid {colors['primary']};
            }}

            /* List Widget */
            QListWidget {{
                background-color: {colors['secondary_background']};
                color: {colors['on_background']};
                border: none;
                border-radius: 4px;
                padding: 5px;
                outline: none;
            }}

            QListWidget::item {{
                background-color: {colors['secondary_background']};
                color: {colors['on_background']};
                padding: 8px;
                border-radius: 4px;
            }}

            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
            }}

            QListWidget::item:hover {{
                background-color: {colors['hover']};
            }}

            /* Scroll Bars */
            QScrollBar:vertical {{
                background: {colors['background']};
                width: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {colors['surface']};
                min-height: 20px;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {colors['hover']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background: {colors['background']};
                height: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:horizontal {{
                background: {colors['surface']};
                min-width: 20px;
                border-radius: 5px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background: {colors['hover']};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* Frames */
            QFrame[panel="true"] {{
                background-color: {colors['surface']};
                border-radius: 8px;
                padding: 10px;
            }}
        """


class TrackProgressBar(QWidget):
    """
    Custom progress bar for displaying track progress with seeking capability.
    Includes time display for current position and track duration.
    """

    # Signal emitted when the user drags the slider to seek
    seek_position = pyqtSignal(int)  # Position in milliseconds

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the track progress bar.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._position_ms = 0
        self._duration_ms = 0
        self._is_seeking = False
        self._theme = Theme.DARK

        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        self.setMinimumHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)

        # Current position label
        self._position_label = QLabel("0:00")
        self._position_label.setMinimumWidth(50)
        self._position_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Progress slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 1000)  # We'll map the actual ms values to this range for smoother UI
        self._slider.setValue(0)
        self._slider.setTracking(True)
        self._slider.sliderPressed.connect(self._on_slider_pressed)
        self._slider.sliderReleased.connect(self._on_slider_released)
        self._slider.valueChanged.connect(self._on_slider_value_changed)
        self._slider.setAccessibleName("Track progress")
        self._slider.setToolTip("Drag to seek through the track")

        # Duration label
        self._duration_label = QLabel("0:00")
        self._duration_label.setMinimumWidth(50)
        self._duration_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add widgets to layout
        layout.addWidget(self._position_label)
        layout.addWidget(self._slider, 1)  # Make slider expand to fill space
        layout.addWidget(self._duration_label)

        # Set the layout
        self.setLayout(layout)

    def set_position(self, position_ms: int) -> None:
        """
        Set the current position.

        Args:
            position_ms (int): Current position in milliseconds
        """
        if not self._is_seeking:
            self._position_ms = max(0, min(position_ms, self._duration_ms))
            self._update_position_label()

            # Update slider position (map to 0-1000 range)
            if self._duration_ms > 0:
                self._slider.setValue(int(self._position_ms / self._duration_ms * 1000))
            else:
                self._slider.setValue(0)

    def set_duration(self, duration_ms: int) -> None:
        """
        Set the track duration.

        Args:
            duration_ms (int): Track duration in milliseconds
        """
        self._duration_ms = max(0, duration_ms)
        self._update_duration_label()

        # Make sure position doesn't exceed duration
        if self._position_ms > self._duration_ms:
            self.set_position(self._duration_ms)

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QLabel {{
                color: {colors['on_background']};
                font-size: 12px;
            }}

            QSlider::groove:horizontal {{
                height: 6px;
                background: {colors['slider_track']};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {colors['slider_handle']};
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {colors['primary']};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}

            QSlider::sub-page:horizontal {{
                background: {colors['progress_bar']};
                border-radius: 3px;
            }}
        """

    def _update_position_label(self) -> None:
        """Update the position label with the current time."""
        self._position_label.setText(self._format_time(self._position_ms))

    def _update_duration_label(self) -> None:
        """Update the duration label with the track duration."""
        self._duration_label.setText(self._format_time(self._duration_ms))

    def _format_time(self, ms: int) -> str:
        """
        Format milliseconds to a time string (M:SS or H:MM:SS).

        Args:
            ms (int): Time in milliseconds

        Returns:
            str: Formatted time string
        """
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60

        if hours > 0:
            return f"{hours}:{minutes % 60:02d}:{seconds % 60:02d}"
        else:
            return f"{minutes}:{seconds % 60:02d}"

    def _on_slider_pressed(self) -> None:
        """Handle the slider being pressed (start seeking)."""
        self._is_seeking = True

    def _on_slider_released(self) -> None:
        """Handle the slider being released (end seeking and apply new position)."""
        if self._is_seeking and self._duration_ms > 0:
            # Map slider value (0-1000) back to actual position in ms
            position = int(self._slider.value() / 1000 * self._duration_ms)
            self._position_ms = position
            self._update_position_label()

            # Emit the seek signal
            self.seek_position.emit(position)

        self._is_seeking = False

    def _on_slider_value_changed(self, value: int) -> None:
        """
        Handle the slider value changing.

        Args:
            value (int): New slider value (0-1000)
        """
        if self._is_seeking and self._duration_ms > 0:
            # Map slider value (0-1000) to actual position in ms
            position = int(value / 1000 * self._duration_ms)
            self._position_ms = position
            self._update_position_label()

    def keyPressEvent(self, event: QMouseEvent) -> None:
        """
        Handle keyboard events for accessibility.

        Args:
            event (QMouseEvent): Keyboard event
        """
        step = 5000  # 5 seconds step for arrow keys

        if event.key() == Qt.Key_Left:
            # Move backward
            new_position = max(0, self._position_ms - step)
            self.set_position(new_position)
            self.seek_position.emit(new_position)
        elif event.key() == Qt.Key_Right:
            # Move forward
            new_position = min(self._duration_ms, self._position_ms + step)
            self.set_position(new_position)
            self.seek_position.emit(new_position)
        else:
            # For any other key, call the parent class handler
            super().keyPressEvent(event)


class VolumeSlider(QWidget):
    """
    Custom volume slider with mute functionality and visual indicators.
    """

    # Signal emitted when the volume level changes
    volume_changed = pyqtSignal(int)  # Volume level (0-100)

    # Signal emitted when mute state changes
    mute_toggled = pyqtSignal(bool)  # True if muted, False otherwise

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the volume slider.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._volume = 100
        self._muted = False
        self._previous_volume = 100  # To restore volume when unmuting
        self._theme = Theme.DARK

        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Mute button
        self._mute_button = QPushButton()
        self._mute_button.setFixedSize(24, 24)
        self._mute_button.setFocusPolicy(Qt.StrongFocus)
        self._mute_button.setToolTip("Mute/Unmute")
        self._mute_button.setAccessibleName("Mute toggle button")
        self._mute_button.clicked.connect(self._on_mute_clicked)

        # Volume slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 100)
        self._slider.setValue(self._volume)
        self._slider.setTracking(True)
        self._slider.valueChanged.connect(self._on_slider_value_changed)
        self._slider.setAccessibleName("Volume slider")
        self._slider.setToolTip(f"Volume: {self._volume}%")

        # Volume level indicator
        self._volume_label = QLabel(f"{self._volume}%")
        self._volume_label.setMinimumWidth(40)
        self._volume_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Add widgets to layout
        layout.addWidget(self._mute_button)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._volume_label)

        # Set the layout
        self.setLayout(layout)

        # Update the button icon based on initial state
        self._update_mute_button()

    def get_volume(self) -> int:
        """
        Get the current volume level.

        Returns:
            int: Volume level (0-100)
        """
        return self._volume

    def set_volume(self, volume: int) -> None:
        """
        Set the volume level.

        Args:
            volume (int): Volume level (0-100)
        """
        volume = max(0, min(100, volume))

        if volume != self._volume:
            self._volume = volume
            self._slider.setValue(volume)
            self._volume_label.setText(f"{volume}%")
            self._slider.setToolTip(f"Volume: {volume}%")

            # If setting volume to 0, update mute button to show muted state
            if volume == 0 and not self._muted:
                self._muted = True
                self._update_mute_button()
                self.mute_toggled.emit(True)
            # If setting volume above 0 and muted, unmute
            elif volume > 0 and self._muted:
                self._muted = False
                self._update_mute_button()
                self.mute_toggled.emit(False)

            self.volume_changed.emit(volume)

    def is_muted(self) -> bool:
        """
        Check if volume is muted.

        Returns:
            bool: True if muted, False otherwise
        """
        return self._muted

    def set_muted(self, muted: bool) -> None:
        """
        Set the mute state.

        Args:
            muted (bool): True to mute, False to unmute
        """
        if muted != self._muted:
            self._muted = muted

            if muted:
                self._previous_volume = self._volume if self._volume > 0 else 100
                self._slider.setValue(0)
            else:
                # Restore previous volume if unmuting
                self._slider.setValue(self._previous_volume)

            self._update_mute_button()
            self.mute_toggled.emit(muted)

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self._update_mute_button()
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QLabel {{
                color: {colors['on_background']};
                font-size: 12px;
            }}

            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                padding: 2px;
            }}

            QPushButton:hover {{
                background-color: {colors['hover']};
            }}

            QPushButton:pressed {{
                background-color: {colors['pressed']};
            }}

            QSlider::groove:horizontal {{
                height: 4px;
                background: {colors['slider_track']};
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                background: {colors['slider_handle']};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {colors['primary']};
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}

            QSlider::sub-page:horizontal {{
                background: {colors['progress_bar']};
                border-radius: 2px;
            }}
        """

    def _update_mute_button(self) -> None:
        """Update the mute button icon based on the current state."""
        if self._muted:
            self._mute_button.setText("🔇")  # Muted icon
            self._mute_button.setToolTip("Unmute")
        else:
            # Different icons based on volume level
            if self._volume >= 70:
                self._mute_button.setText("🔊")  # High volume icon
            elif self._volume >= 30:
                self._mute_button.setText("🔉")  # Medium volume icon
            else:
                self._mute_button.setText("🔈")  # Low volume icon

            self._mute_button.setToolTip("Mute")

    def _on_mute_clicked(self) -> None:
        """Toggle mute state when the mute button is clicked."""
        self.set_muted(not self._muted)

    def _on_slider_value_changed(self, value: int) -> None:
        """
        Handle the slider value changing.

        Args:
            value (int): New volume level (0-100)
        """
        self._volume = value
        self._volume_label.setText(f"{value}%")
        self._slider.setToolTip(f"Volume: {value}%")

        # Update mute state based on volume
        if value == 0 and not self._muted:
            self._muted = True
            self._update_mute_button()
            self.mute_toggled.emit(True)
        elif value > 0 and self._muted:
            self._muted = False
            self._update_mute_button()
            self.mute_toggled.emit(False)

        self.volume_changed.emit(value)

    def keyPressEvent(self, event: QMouseEvent) -> None:
        """
        Handle keyboard events for accessibility.

        Args:
            event (QMouseEvent): Keyboard event
        """
        step = 5  # 5% step for arrow keys

        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Right:
            # Increase volume
            self.set_volume(self._volume + step)
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_Left:
            # Decrease volume
            self.set_volume(self._volume - step)
        elif event.key() == Qt.Key_M:
            # Toggle mute
            self.set_muted(not self._muted)
        else:
            # For any other key, call the parent class handler
            super().keyPressEvent(event)


class MediaControls(QWidget):
    """
    Widget containing media playback controls (play, pause, stop, next, previous, etc.).
    """

    # Signals for button clicks
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    previous_clicked = pyqtSignal()
    shuffle_toggled = pyqtSignal(bool)
    repeat_mode_changed = pyqtSignal(int)  # 0: No repeat, 1: Repeat playlist, 2: Repeat track

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the media controls.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._is_playing = False
        self._shuffle_on = False
        self._repeat_mode = 0  # 0: No repeat, 1: Repeat playlist, the_current_playlistt track
        self._theme = Theme.DARK

        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Previous track button
        self._prev_button = QPushButton("⏮")
        self._prev_button.setToolTip("Previous track")
        self._prev_button.setAccessibleName("Previous track")
        self._prev_button.setFixedSize(40, 40)
        self._prev_button.clicked.connect(self.previous_clicked.emit)

        # Play/Pause button
        self._play_pause_button = QPushButton("▶")
        self._play_pause_button.setToolTip("Play")
        self._play_pause_button.setAccessibleName("Play/Pause")
        self._play_pause_button.setFixedSize(50, 50)
        self._play_pause_button.clicked.connect(self._on_play_pause_clicked)
        # Stop button
        self._stop_button = QPushButton("⏹")
        self._stop_button.setToolTip("Stop")
        self._stop_button.setAccessibleName("Stop")
        self._stop_button.setFixedSize(40, 40)
        self._stop_button.clicked.connect(self.stop_clicked.emit)

        # Next track button
        self._next_button = QPushButton("⏭")
        self._next_button.setToolTip("Next track")
        self._next_button.setAccessibleName("Next track")
        self._next_button.setFixedSize(40, 40)
        self._next_button.clicked.connect(self.next_clicked.emit)

        # Shuffle button
        self._shuffle_button = QPushButton("🔀")
        self._shuffle_button.setToolTip("Shuffle off")
        self._shuffle_button.setAccessibleName("Toggle shuffle")
        self._shuffle_button.setFixedSize(40, 40)
        self._shuffle_button.setCheckable(True)
        self._shuffle_button.clicked.connect(self._on_shuffle_clicked)

        # Repeat button
        self._repeat_button = QPushButton("🔁")
        self._repeat_button.setToolTip("Repeat off")
        self._repeat_button.setAccessibleName("Toggle repeat mode")
        self._repeat_button.setFixedSize(40, 40)
        self._repeat_button.clicked.connect(self._on_repeat_clicked)

        # Add spacing with stretches
        layout.addStretch(1)
        layout.addWidget(self._shuffle_button)
        layout.addWidget(self._prev_button)
        layout.addWidget(self._stop_button)
        layout.addWidget(self._play_pause_button)
        layout.addWidget(self._next_button)
        layout.addWidget(self._repeat_button)
        layout.addStretch(1)

        # Set the layout
        self.setLayout(layout)

        # Apply initial styles
        self.setStyleSheet(self._get_style())

    def set_playing_state(self, is_playing: bool) -> None:
        """
        Set the playing state and update the play/pause button.

        Args:
            is_playing (bool): True if playing, False if paused
        """
        if is_playing != self._is_playing:
            self._is_playing = is_playing
            self._update_button_states()

    def set_shuffle_state(self, shuffle_on: bool) -> None:
        """
        Set the shuffle state and update the shuffle button.

        Args:
            shuffle_on (bool): True to enable shuffle, False to disable
        """
        if shuffle_on != self._shuffle_on:
            self._shuffle_on = shuffle_on
            self._shuffle_button.setChecked(shuffle_on)
            self._update_button_states()

    def set_repeat_mode(self, mode: int) -> None:
        """
        Set the repeat mode and update the repeat button.

        Args:
            mode (int): Repeat mode (0=No repeat, 1=Repeat playlist, 2=Repeat track)
        """
        if mode != self._repeat_mode:
            self._repeat_mode = mode
            self._update_button_states()

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QPushButton {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                border: none;
                border-radius: 20px;
                font-size: 18px;
                padding: 5px;
            }}

            QPushButton:hover {{
                background-color: {colors['hover']};
            }}

            QPushButton:pressed {{
                background-color: {colors['pressed']};
            }}

            QPushButton:checked {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
            }}

            QPushButton#play_pause {{
                font-size: 22px;
            }}
        """

    def _on_play_pause_clicked(self) -> None:
        """Handle the play/pause button being clicked."""
        if self._is_playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()

    def _on_shuffle_clicked(self) -> None:
        """Handle the shuffle button being toggled."""
        self._shuffle_on = self._shuffle_button.isChecked()

        # Update tooltip
        if self._shuffle_on:
            self._shuffle_button.setToolTip("Shuffle on")
        else:
            self._shuffle_button.setToolTip("Shuffle off")

        self.shuffle_toggled.emit(self._shuffle_on)

    def _on_repeat_clicked(self) -> None:
        modes = list(RepeatMode)
        current_index = modes.index(self._repeat_mode)
        next_index = (current_index + 1) % len(modes)
        self._repeat_mode = modes[next_index]

        self._update_button_states()
        self.repeat_mode_changed.emit(self._repeat_mode)

    def _update_button_states(self) -> None:
        """Update button appearances based on current states."""
        # Update play/pause button
        if self._is_playing:
            self._play_pause_button.setText("⏸")
            self._play_pause_button.setToolTip("Pause")
        else:
            self._play_pause_button.setText("▶")
            self._play_pause_button.setToolTip("Play")

        # Update shuffle button
        self._shuffle_button.setChecked(self._shuffle_on)

        # Update repeat button text and tooltip based on mode
        if self._repeat_mode == 0:  # No repeat
            self._repeat_button.setText("🔁")
            self._repeat_button.setToolTip("Repeat off")
            self._repeat_button.setChecked(False)
        elif self._repeat_mode == 1:  # Repeat playlist
            self._repeat_button.setText("🔁")
            self._repeat_button.setToolTip("Repeat playlist")
            self._repeat_button.setChecked(True)
        else:  # Repeat track
            self._repeat_button.setText("🔂")
            self._repeat_button.setToolTip("Repeat track")
            self._repeat_button.setChecked(True)

    def keyPressEvent(self, event: QMouseEvent) -> None:
        """
        Handle keyboard events for accessibility.

        Args:
            event (QMouseEvent): Keyboard event
        """
        if event.key() == Qt.Key_Space:
            # Toggle play/pause with space bar
            self._on_play_pause_clicked()
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            # Toggle shuffle with Ctrl+S
            self._shuffle_button.click()
        elif event.key() == Qt.Key_R and event.modifiers() == Qt.ControlModifier:
            # Toggle repeat mode with Ctrl+R
            self._on_repeat_clicked()
        elif event.key() == Qt.Key_Left and event.modifiers() == Qt.ControlModifier:
            # Previous track with Ctrl+Left
            self.previous_clicked.emit()
        elif event.key() == Qt.Key_Right and event.modifiers() == Qt.ControlModifier:
            # Next track with Ctrl+Right
            self.next_clicked.emit()
        elif event.key() == Qt.Key_MediaStop:
            # Stop with media key
            self.stop_clicked.emit()
        elif event.key() == Qt.Key_MediaPlay or event.key() == Qt.Key_MediaPause or event.key() == Qt.Key_MediaTogglePlayPause:
            # Play/Pause with media keys
            self._on_play_pause_clicked()
        elif event.key() == Qt.Key_MediaPrevious:
            # Previous track with media key
            self.previous_clicked.emit()
        elif event.key() == Qt.Key_MediaNext:
            # Next track with media key
            self.next_clicked.emit()
        else:
            # For any other key, call the parent class handler
            super().keyPressEvent(event)


class PlaylistView(QListWidget):
    """
    Custom QListWidget for displaying and managing playlists with drag-and-drop support.
    Includes custom rendering of track information and album art thumbnails.
    """

    # Signal emitted when a track is double-clicked
    track_double_clicked = pyqtSignal(int)  # Track index

    # Signal emitted when tracks are reordered via drag and drop
    tracks_reordered = pyqtSignal(int, int)  # from_index, to_index

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the playlist view.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._theme = Theme.DARK
        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        # Enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Connect signals
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Set item delegate for custom rendering
        self.setItemDelegate(PlaylistItemDelegate(self))

        # Apply styling
        self.setStyleSheet(self._get_style())

    def add_track(self, title: str, artist: str, duration: str, album_art: Optional[QPixmap] = None) -> QListWidgetItem:
        """
        Add a track to the playlist view.

        Args:
            title (str): Track title
            artist (str): Artist name
            duration (str): Formatted duration string
            album_art (Optional[QPixmap]): Album art thumbnail

        Returns:
            QListWidgetItem: The created list item
        """
        item = QListWidgetItem(self)

        # Store track data as item data
        item_data = {
            'title': title,
            'artist': artist,
            'duration': duration,
            'album_art': album_art
        }

        item.setData(Qt.UserRole, item_data)

        # Set text for basic display and search
        item.setText(f"{title} - {artist}")

        # Set size hint for proper layout
        item.setSizeHint(QSize(self.width() - 20, 60))

        self.addItem(item)
        return item

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self.setStyleSheet(self._get_style())

        # Update all items to refresh their appearance
        for i in range(self.count()):
            item = self.item(i)
            item.setData(Qt.UserRole, item.data(Qt.UserRole))

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QListWidget {{
                background-color: {colors['secondary_background']};
                color: {colors['on_background']};
                border: none;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }}

            QListWidget::item {{
                background-color: {colors['secondary_background']};
                color: {colors['on_background']};
                border-radius: 4px;
                padding: 5px;
                margin: 2px 5px;
            }}

            QListWidget::item:selected {{
                background-color: {colors['primary']};
                color: {colors['on_primary']};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {colors['hover']};
            }}
        """

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """
        Handle an item being double-clicked.

        Args:
            item (QListWidgetItem): The clicked item
        """
        index = self.row(item)
        self.track_double_clicked.emit(index)

    def _show_context_menu(self, position: QPoint) -> None:
        """
        Show a context menu for playlist operations.

        Args:
            position (QPoint): Position where to show the menu
        """
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Add actions
        play_action = menu.addAction("Play")
        menu.addSeparator()
        remove_action = menu.addAction("Remove from playlist")
        menu.addSeparator()
        info_action = menu.addAction("Track info")

        # Show menu and handle actions
        action = menu.exec_(self.mapToGlobal(position))

        if action == play_action:
            self.track_double_clicked.emit(self.row(item))
        elif action == remove_action:
            pass
        elif action == info_action:
            track_data = item.data(Qt.UserRole)
            self._show_track_info_dialog(track_data)

    def _show_track_info_dialog(self, track_data: Dict[str, Any]) -> None:
        """
        Show a dialog with detailed track information.

        Args:
            track_data (Dict[str, Any]): Track data dictionary
        """
        # Create a simple dialog to display track info
        dialog = QDialog(self)
        dialog.setWindowTitle("Track Information")
        dialog.setMinimumSize(400, 300)

        # Create layout
        layout = QVBoxLayout(dialog)

        # Add track info
        title_label = QLabel(f"<b>Title:</b> {track_data.get('title', 'Unknown')}")
        artist_label = QLabel(f"<b>Artist:</b> {track_data.get('artist', 'Unknown')}")
        duration_label = QLabel(f"<b>Duration:</b> {track_data.get('duration', 'Unknown')}")

        # Add album art if available
        album_art = track_data.get('album_art')
        if album_art:
            art_label = QLabel()
            art_label.setPixmap(album_art.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            art_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(art_label)

        # Add labels to layout
        layout.addWidget(title_label)
        layout.addWidget(artist_label)
        layout.addWidget(duration_label)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button, 0, Qt.AlignRight)

        # Apply theme
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                color: {colors['on_background']};
            }}
            QLabel {{
                color: {colors['on_background']};
                padding: 5px;
            }}
            QPushButton {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
            }}
        """)

        # Show dialog
        dialog.exec_()

    def keyPressEvent(self, event: QMouseEvent) -> None:
        """
        Handle keyboard events for playlist navigation.

        Args:
            event (QMouseEvent): Keyboard event
        """
        if event.key() == Qt.Key_Delete:
            # Remove selected tracks
            selected_items = self.selectedItems()
            for item in reversed(selected_items):  # Remove from bottom to top to avoid index issues
                self.takeItem(self.row(item))
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Play selected track
            current_item = self.currentItem()
            if current_item:
                self.track_double_clicked.emit(self.row(current_item))
        else:
            # For any other key, call the parent class handler
            super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Handle drop events for drag and drop reordering.

        Args:
            event (QDropEvent): Drop event
        """
        if event.source() == self:
            # Get the drop position
            drop_pos = event.pos()
            drop_item = self.itemAt(drop_pos)

            if drop_item:
                drop_index = self.row(drop_item)

                # Get the dragged item
                dragged_items = self.selectedItems()
                if dragged_items:
                    # Handle only the first dragged item for now
                    dragged_item = dragged_items[0]
                    from_index = self.row(dragged_item)

                    # Skip if dropping on itself
                    if from_index == drop_index:
                        event.ignore()
                        return

                    # Let the parent handle the actual move
                    super().dropEvent(event)

                    # Emit signal for the reordering
                    self.tracks_reordered.emit(from_index, drop_index)
                    return

        # For other drop types, call the parent handler
        super().dropEvent(event)


class PlaylistItemDelegate(QStyledItemDelegate):
    """
    Custom delegate for rendering playlist items with album art and track information.
    """

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Initialize the playlist item delegate.

        Args:
            parent (Optional[QObject]): Parent object, if any
        """
        super().__init__(parent)
        self._theme = Theme.DARK

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        Paint the delegate for the item at the given index.

        Args:
            painter (QPainter): Painter to use for rendering
            option (QStyleOptionViewItem): Style options for rendering
            index (QModelIndex): Model index of the item to render
        """
        # Get the item data
        track_data = index.data(Qt.UserRole)
        if not track_data:
            super().paint(painter, option, index)
            return

        # Prepare colors based on item state and theme
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        # Set background color based on selection state
        if option.state & QStyle.State_Selected:
            background_color = QColor(colors['primary'])
            text_color = QColor(colors['on_primary'])
        elif option.state & QStyle.State_MouseOver:
            background_color = QColor(colors['hover'])
            text_color = QColor(colors['on_background'])
        else:
            background_color = QColor(colors['secondary_background'])
            text_color = QColor(colors['on_background'])

        # Draw background
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawRoundedRect(option.rect, 4, 4)

        # Calculate item layout
        rect = option.rect
        padding = 5
        album_art_size = rect.height() - (padding * 2)

        # Draw album art if available
        album_art = track_data.get('album_art')
        if album_art:
            art_rect = QRect(rect.left() + padding, rect.top() + padding, album_art_size, album_art_size)
            painter.drawPixmap(art_rect, album_art.scaled(album_art_size, album_art_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Calculate text area
        text_rect = QRect(
            rect.left() + album_art_size + (padding * 2),
            rect.top() + padding,
            rect.width() - album_art_size - (padding * 4) - 60,  # Reserve space for duration
            rect.height() - (padding * 2)
        )

        # Draw track title and artist
        painter.setPen(text_color)

        # Title - Bold, larger font
        title_font = painter.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 1)
        painter.setFont(title_font)

        title = track_data.get('title', 'Unknown Title')
        painter.drawText(
            text_rect.left(),
            text_rect.top() + 15,
            text_rect.width(),
            20,
            Qt.AlignLeft | Qt.AlignTop,
            title
        )

        # Artist - Normal font
        artist_font = painter.font()
        artist_font.setBold(False)
        artist_font.setPointSize(artist_font.pointSize() - 1)
        painter.setFont(artist_font)

        artist = track_data.get('artist', 'Unknown Artist')
        painter.drawText(
            text_rect.left(),
            text_rect.top() + 35,
            text_rect.width(),
            20,
            Qt.AlignLeft | Qt.AlignTop,
            artist
        )

        # Draw duration
        duration = track_data.get('duration', '')
        painter.drawText(
            rect.right() - 60 - padding,
            rect.top() + padding,
            60,
            rect.height() - (padding * 2),
            Qt.AlignRight | Qt.AlignVCenter,
            duration
        )

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """
        Get the size hint for the item at the given index.

        Args:
            option (QStyleOptionViewItem): Style options
            index (QModelIndex): Model index of the item

        Returns:
            QSize: Suggested size for the item
        """
        return QSize(option.rect.width(), 60)

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme


class TrackInfoPanel(QWidget):
    """
    Panel for displaying current track information and album art.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the track info panel.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._theme = Theme.DARK
        self._current_track_data: Dict[str, Any] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Album art display
        self._album_art_frame = QFrame()
        self._album_art_frame.setMinimumSize(250, 250)
        self._album_art_frame.setMaximumSize(400, 400)
        self._album_art_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        album_art_layout = QVBoxLayout(self._album_art_frame)
        album_art_layout.setContentsMargins(0, 0, 0, 0)

        self._album_art_label = QLabel()
        self._album_art_label.setAlignment(Qt.AlignCenter)
        self._album_art_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._album_art_label.setMinimumSize(200, 200)
        self._album_art_label.setText("No Track Playing")
        self._album_art_label.setStyleSheet("font-size: 16px; color: rgba(255, 255, 255, 0.5);")

        album_art_layout.addWidget(self._album_art_label)

        # Track metadata display
        self._metadata_frame = QFrame()
        metadata_layout = QVBoxLayout(self._metadata_frame)
        metadata_layout.setContentsMargins(0, 10, 0, 0)
        metadata_layout.setSpacing(5)

        # Title
        self._title_label = QLabel("No Track Selected")
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setProperty("title", "true")

        # Artist
        self._artist_label = QLabel("—")
        self._artist_label.setAlignment(Qt.AlignCenter)
        self._artist_label.setStyleSheet("font-size: 14px;")

        # Album
        self._album_label = QLabel("—")
        self._album_label.setAlignment(Qt.AlignCenter)
        self._album_label.setStyleSheet("font-size: 12px;")

        # Additional metadata in a grid
        metadata_grid = QFrame()
        grid_layout = QVBoxLayout(metadata_grid)
        grid_layout.setContentsMargins(0, 10, 0, 0)
        grid_layout.setSpacing(5)

        # Genre
        self._genre_row = QHBoxLayout()
        self._genre_label_title = QLabel("Genre:")
        self._genre_label_title.setStyleSheet("font-weight: bold; min-width: 80px;")
        self._genre_label = QLabel("—")
        self._genre_row.addWidget(self._genre_label_title)
        self._genre_row.addWidget(self._genre_label, 1)

        # Year
        self._year_row = QHBoxLayout()
        self._year_label_title = QLabel("Year:")
        self._year_label_title.setStyleSheet("font-weight: bold; min-width: 80px;")
        self._year_label = QLabel("—")
        self._year_row.addWidget(self._year_label_title)
        self._year_row.addWidget(self._year_label, 1)

        # Bitrate
        self._bitrate_row = QHBoxLayout()
        self._bitrate_label_title = QLabel("Bitrate:")
        self._bitrate_label_title.setStyleSheet("font-weight: bold; min-width: 80px;")
        self._bitrate_label = QLabel("—")
        self._bitrate_row.addWidget(self._bitrate_label_title)
        self._bitrate_row.addWidget(self._bitrate_label, 1)

        # Add rows to grid
        grid_layout.addLayout(self._genre_row)
        grid_layout.addLayout(self._year_row)
        grid_layout.addLayout(self._bitrate_row)

        metadata_layout.addWidget(self._title_label)
        metadata_layout.addWidget(self._artist_label)
        metadata_layout.addWidget(self._album_label)
        metadata_layout.addWidget(metadata_grid)

        # Create a scroll area for overflow
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Add main widgets to the layout
        layout.addWidget(self._album_art_frame)
        layout.addWidget(self._metadata_frame)

        # Apply styling
        self.setStyleSheet(self._get_style())

        # Clear display initially
        self.clear_display()

    def update_track_info(self, track_data: Dict[str, Any]) -> None:
        """
        Update the panel with new track information.

        Args:
            track_data (Dict[str, Any]): Dictionary containing track metadata
        """
        self._current_track_data = track_data
        self._update_display()

    def clear_display(self) -> None:
        """Clear all track information and display the default state."""
        self._current_track_data = {}

        # Reset labels
        self._title_label.setText("No Track Selected")
        self._artist_label.setText("—")
        self._album_label.setText("—")
        self._genre_label.setText("—")
        self._year_label.setText("—")
        self._bitrate_label.setText("—")

        # Reset album art
        self._album_art_label.setPixmap(QPixmap())
        self._album_art_label.setText("No Track Playing")

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QFrame {{
                background-color: transparent;
            }}

            QLabel {{
                color: {colors['on_background']};
            }}

            QLabel[title="true"] {{
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }}

            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """

    def _update_display(self) -> None:
        """Update UI components with the current track data."""
        if not self._current_track_data:
            self.clear_display()
            return

        # Update title, artist, album
        title = self._current_track_data.get('title', 'Unknown Title')
        artist = self._current_track_data.get('artist', 'Unknown Artist')
        album = self._current_track_data.get('album', 'Unknown Album')

        # Asegurarse de que sean cadenas de texto
        if isinstance(title, list):
            title = ', '.join(title)
        if isinstance(artist, list):
            artist = ', '.join(artist)
        if isinstance(album, list):
            album = ', '.join(album)

        self._title_label.setText(title)
        self._artist_label.setText(artist)
        self._album_label.setText(album)


        # Update additional metadata
        genre = self._current_track_data.get('genre', '—')
        year = self._current_track_data.get('year', '—')

        # Convertir listas a texto legible
        if isinstance(genre, list):
            genre = ', '.join(genre)
        if isinstance(year, list):
            year = ', '.join(str(y) for y in year)

        self._genre_label.setText(genre)
        self._year_label.setText(str(year))

        # Format and update bitrate
        bitrate = self._current_track_data.get('bitrate')
        if bitrate:
            self._bitrate_label.setText(self._format_bitrate(bitrate))
        else:
            self._bitrate_label.setText('—')

        # Update album art
        album_art = self._current_track_data.get('album_art')
        if album_art:
            self._album_art_label.setText("")  # Clear the text
            pixmap = QPixmap(album_art)
            if not pixmap.isNull():
                # Scale pixmap to fit the label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self._album_art_label.width(),
                    self._album_art_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self._album_art_label.setPixmap(scaled_pixmap)
            else:
                self._album_art_label.setText("No Album Art")
        else:
            self._album_art_label.setPixmap(QPixmap())
            self._album_art_label.setText("No Album Art")

    def _format_bitrate(self, bitrate: int) -> str:
        """
        Format bitrate value into human-readable format.

        Args:
            bitrate (int): Bitrate in bits per second

        Returns:
            str: Formatted bitrate string
        """
        if bitrate >= 1000000:
            return f"{bitrate / 1000000:.2f} Mbps"
        else:
            return f"{bitrate / 1000:.0f} kbps"

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Handle resize events to update the album art size.

        Args:
            event (QResizeEvent): Resize event
        """
        super().resizeEvent(event)

        # If we have album art, rescale it
        if self._current_track_data.get('album_art') and not self._album_art_label.pixmap().isNull():
            self._update_display()


class SearchBar(QWidget):
    """
    Custom search bar for filtering tracks in playlists.
    """

    # Signal emitted when the search text changes
    search_text_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the search bar.

        Args:
            parent (Optional[QWidget]): Parent widget, if any
        """
        super().__init__(parent)

        self._theme = Theme.DARK
        self._init_ui()

    def _init_ui(self) -> None:
        """Set up the user interface components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Search icon or label
        self._search_icon = QLabel("🔍")
        self._search_icon.setFixedSize(20, 20)
        self._search_icon.setAlignment(Qt.AlignCenter)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_input.setAccessibleName("Search input")

        # Add widgets to layout
        layout.addWidget(self._search_icon)
        layout.addWidget(self._search_input, 1)

        # Apply styling
        self.setStyleSheet(self._get_style())

    def get_search_text(self) -> str:
        """
        Get the current search text.

        Returns:
            str: Current search text
        """
        return self._search_input.text()

    def set_search_text(self, text: str) -> None:
        """
        Set the search text.

        Args:
            text (str): Search text to set
        """
        self._search_input.setText(text)

    def clear_search(self) -> None:
        """Clear the search input."""
        self._search_input.clear()

    def set_theme(self, theme: Theme) -> None:
        """
        Set the color theme.

        Args:
            theme (Theme): Color theme to apply
        """
        self._theme = theme
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        """
        Get the stylesheet for this widget.

        Returns:
            str: CSS stylesheet
        """
        if self._theme == Theme.DARK:
            colors = ColorScheme.DARK
        else:
            colors = ColorScheme.LIGHT

        return f"""
            QLineEdit {{
                background-color: {colors['surface']};
                color: {colors['on_surface']};
                border: 1px solid {colors['border']};
                border-radius: 15px;
                padding: 5px 10px;
                font-size: 14px;
            }}

            QLineEdit:focus {{
                border: 1px solid {colors['primary']};
            }}

            QLabel {{
                color: {colors['on_background']};
                font-size: 14px;
            }}
        """

    def _on_search_text_changed(self, text: str) -> None:
        """
        Handle search text changes.

        Args:
            text (str): New search text
        """
        self.search_text_changed.emit(text)
