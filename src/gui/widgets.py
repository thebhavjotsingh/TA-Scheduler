"""
Custom GUI widgets for the TA Scheduler application.
"""
import os
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFileDialog, QMessageBox, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor, QFont
from PySide6.QtCore import Qt

from ..config.constants import DEFAULT_APP_NAME


class ModernFileDropZone(QFrame):
    """
    A modern, enhanced file drop zone with visual feedback and animations.
    """
    fileDropped = None  # Will be set as pyqtSignal later
    
    def __init__(self, title="Drop CSV file here", subtitle="or click to browse", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.file_path = ""
        self.is_dragging = False
        
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)  # Increased from 100 to 150
        self.setMinimumWidth(250)   # Added minimum width
        self.setFrameStyle(QFrame.StyledPanel)
        self.setProperty("class", "file-drop")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # File icon (using text for now, can be replaced with actual icons)
        self.icon_label = QLabel("📁")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setProperty("class", "file-icon")
        self.icon_label.setScaledContents(True)  # Allow scaling
        
        # Set initial responsive font size
        self.update_icon_size()
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setProperty("class", "file-title")
        self.title_label.setWordWrap(False)  # Prevent wrapping
        
        # Subtitle label
        self.subtitle_label = QLabel(self.subtitle)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setProperty("class", "file-subtitle")
        self.subtitle_label.setWordWrap(False)  # Prevent wrapping
        
        # File path label (hidden initially)
        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setProperty("class", "file-path")
        self.path_label.setWordWrap(False)  # Prevent wrapping to avoid expansion
        self.path_label.hide()
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.path_label)
        
        # Add shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow_effect)
        
        # Click to browse
        self.mousePressEvent = self.handle_click

    def update_icon_size(self):
        """Update the icon size based on the widget's current size"""
        # Calculate responsive font size based on widget dimensions
        widget_height = self.height() if self.height() > 0 else 100
        widget_width = self.width() if self.width() > 0 else 200
        
        # Use the smaller dimension to maintain aspect ratio
        base_size = min(widget_height, widget_width)
        
        # Scale the font size (adjust the multiplier as needed)
        font_size = max(16, int(base_size * 0.15))  # Minimum 16px, scales with widget
        
        # Apply the font size to the icon
        font = self.icon_label.font()
        font.setPointSize(font_size)
        self.icon_label.setFont(font)

    def resizeEvent(self, event):
        """Handle resize events to update icon size"""
        super().resizeEvent(event)
        self.update_icon_size()

    def showEvent(self, event):
        """Handle show events to ensure icon is properly sized"""
        super().showEvent(event)
        self.update_icon_size()

    def handle_click(self, event):
        """Handle click to open file dialog"""
        if event.button() == Qt.LeftButton:
            self.browse_file()

    def browse_file(self):
        """Open file dialog to select CSV"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV file", "", "CSV files (*.csv)"
        )
        if path and path.lower().endswith('.csv'):
            self.set_file_path(path)

    def set_file_path(self, path):
        """Set the selected file path and update UI with truncated names"""
        self.file_path = path
        filename = path.split('/')[-1] if '/' in path else path.split('\\')[-1]
        
        # Truncate filename if too long (keep extension)
        max_filename_length = 25
        if len(filename) > max_filename_length:
            name_part, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            if ext:
                truncated_name = name_part[:max_filename_length-len(ext)-4] + '...' + '.' + ext
            else:
                truncated_name = filename[:max_filename_length-3] + '...'
            display_filename = truncated_name
        else:
            display_filename = filename
        
        # Truncate full path if too long
        max_path_length = 50
        if len(path) > max_path_length:
            display_path = '...' + path[-(max_path_length-3):]
        else:
            display_path = path
        
        # Update labels
        self.icon_label.setText("✅")
        self.icon_label.setProperty("class", "file-icon success")
        self.update_icon_size()  # Update icon size after changing the icon
        self.title_label.setText(f"Selected: {display_filename}")
        self.subtitle_label.setText("Click to change file")
        self.path_label.setText(display_path)
        self.path_label.show()
        
        # Update styling to show success
        self.setProperty("class", "file-drop-success")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter with visual feedback"""
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if path.lower().endswith('.csv'):
                self.is_dragging = True
                self.setProperty("class", "file-drop-active")
                self.style().unpolish(self)
                self.style().polish(self)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave to reset visual state"""
        self.is_dragging = False
        self.setProperty("class", "file-drop")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        path = event.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith('.csv'):
            self.set_file_path(path)
            event.acceptProposedAction()
        else:
            QMessageBox.warning(self, "Invalid File", "Only .csv files are allowed.")
        
        self.is_dragging = False
        self.setProperty("class", "file-drop")
        self.style().unpolish(self)
        self.style().polish(self)

    def get_file_path(self):
        """Get the current file path"""
        return self.file_path


class ModernCard(QFrame):
    """
    A modern card container with shadow and hover effects.
    """
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setFrameStyle(QFrame.StyledPanel)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 16, 20, 16)
        self.main_layout.setSpacing(12)
        
        # Title if provided
        if title:
            title_label = QLabel(title)
            title_label.setProperty("class", "card-title")
            self.main_layout.addWidget(title_label)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def add_widget(self, widget):
        """Add a widget to the card"""
        self.main_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the card"""
        self.main_layout.addLayout(layout)


class FileDropLineEdit(QTextEdit):
    """
    A QTextEdit subclass that only accepts CSV files via drag-and-drop.

    Overrides dragEnterEvent and dropEvent to filter for .csv files.
    """
    def __init__(self, parent=None):
        """
        Initialize the line edit widget for file dropping.

        Args:
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(25)
        self.setAcceptRichText(False)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter events to accept only CSV files.
        """
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if path.lower().endswith('.csv'):
                event.acceptProposedAction()
            else:
                QMessageBox.warning(self, DEFAULT_APP_NAME, "Only .csv files are allowed.")
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        Handle drop events by inserting the path of the CSV file.
        """
        path = event.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith('.csv'):
            self.setText(path)
        else:
            QMessageBox.warning(self, DEFAULT_APP_NAME, "Only .csv files are allowed.")
        event.acceptProposedAction()
