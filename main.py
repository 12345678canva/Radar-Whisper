#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Main entry point for the application
"""

import argparse
import os
import sys
import traceback
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QCoreApplication, QSettings, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QStyleFactory

from main_window import MainWindow


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Radar Whisper Music Player")

    # Add file or folder argument
    parser.add_argument(
        "path", nargs="?", default=None,
        help="Audio file or folder to open on startup"
    )

    # Add option to disable high DPI scaling
    parser.add_argument(
        "--disable-high-dpi", action="store_true",
        help="Disable high DPI scaling"
    )

    # Add option to force a specific theme
    parser.add_argument(
        "--theme", choices=["dark", "light"], default=None,
        help="Force a specific theme (dark/light)"
    )

    return parser.parse_args()


def setup_high_dpi() -> None:
    """Configure high DPI support for the application."""
    # This must be done before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # For Qt 5.14 and newer
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def setup_application_metadata() -> None:
    """Set up application metadata."""
    QCoreApplication.setOrganizationName("RadarWhisper")
    QCoreApplication.setOrganizationDomain("radarwhisper.com")
    QCoreApplication.setApplicationName("Radar Whisper")
    QCoreApplication.setApplicationVersion("1.0.0")


def setup_exception_hook() -> None:
    """Set up global exception hook for unhandled exceptions."""
    def exception_hook(exc_type, exc_value, exc_traceback):
        """
        Handle uncaught exceptions.

        Args:
            exc_type: Type of the exception
            exc_value: Value of the exception
            exc_traceback: Traceback of the exception
        """
        # Log the error
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Uncaught exception:\n{error_msg}", file=sys.stderr)

        # Show error message to the user if GUI is available
        if QApplication.instance():
            QMessageBox.critical(
                None,
                "Unhandled Exception",
                f"An unhandled exception occurred:\n\n{exc_value}\n\n"
                f"The application might be in an unstable state. "
                f"It's recommended to restart the application."
            )

    # Install exception hook
    sys.excepthook = exception_hook


def main() -> int:
    """
    Main entry point for the Radar Whisper application.

    Returns:
        int: Exit code
    """
    # Parse command line arguments
    args = parse_arguments()

    # Configure high DPI support if not disabled
    if not args.disable_high_dpi:
        setup_high_dpi()

    # Create the application
    app = QApplication(sys.argv)

    # Set up application metadata
    setup_application_metadata()

    # Set up exception hook
    setup_exception_hook()

    # Set up application style and fonts
    app.setStyle(QStyleFactory.create("Fusion"))  # Consistent style across platforms

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Process command line arguments
    if args.path:
        # Check if the path exists
        if os.path.exists(args.path):
            if os.path.isdir(args.path):
                # It's a directory, open it
                window._on_open_folder(args.path)
            else:
                # It's a file, open it
                window._on_open_files([args.path])

    # Run the application event loop
    return app.exec_()


if __name__ == "__main__":
    # Set the current working directory to the script's directory
    if getattr(sys, 'frozen', False):
        # We're running in a bundle (PyInstaller)
        script_dir = os.path.dirname(sys.executable)
    else:
        # We're running in a normal Python environment
        script_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_dir)

    # Run the application and exit with its return code
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar Whisper - A modern music player application
Entry point for the application
"""

import sys

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow


def main() -> None:
    """
    Main entry point for the Radar Whisper application.
    Sets up the QApplication and initializes the main window.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Radar Whisper")
    app.setOrganizationName("Radar Whisper")
    app.setOrganizationDomain("radarwhisper.com")

    # Set up stylesheet (can be loaded from an external file later)
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #121212;
            color: #f0f0f0;
        }
        QPushButton {
            background-color: #272727;
            color: #f0f0f0;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
        }
        QPushButton:pressed {
            background-color: #4a4a4a;
        }
        QSlider::groove:horizontal {
            height: 4px;
            background: #3a3a3a;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #b3b3b3;
            width: 12px;
            height: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }
        QSlider::handle:horizontal:hover {
            background: #f0f0f0;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

