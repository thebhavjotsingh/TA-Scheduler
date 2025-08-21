#!/usr/bin/env python3
"""
TA Scheduler - Main Application Entry Point

A desktop application for assigning TAs to lab sections using Google OR-Tools CP-SAT.
Features:
  - Drag-and-drop or browse CSV file inputs (CSV-only)
  - Constraint Programming optimization using OR-Tools CP-SAT
  - Supports partial slot filling when full coverage isn't possible
  - Enforces no overlapping time slot assignments per TA
  - Limits daily working hours per TA (configurable via MAX_DAILY_HOURS)
  - Optional export of slot and TA summaries to CSV

Dependencies:
  - pandas
  - ortools
  - PySide6
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont

# Add the src directory to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from src.gui.main_window import App
from src.config.constants import DEFAULT_APP_NAME, ICON_PATH
from src.config.styles import DARK_THEME


def main():
    """Main application entry point."""
    # Initialize and run the Qt application with modern dark theme
    app = QApplication(sys.argv)
    app.setApplicationName(DEFAULT_APP_NAME)
    
    # Set application icon if available
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
    
    # Apply dark theme to the entire application
    app.setStyleSheet(DARK_THEME)
    
    # Set modern font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # Create and show the main window
    window = App()
    window.show()
    
    # Center the window on screen
    screen = app.primaryScreen().geometry()
    window.move((screen.width() - window.width()) // 2, 
                (screen.height() - window.height()) // 2)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
