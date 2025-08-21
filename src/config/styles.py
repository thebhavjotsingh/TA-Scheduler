"""
UI styling and themes for the TA Scheduler application.
"""
from .stylesheet_loader import get_theme_stylesheet


def get_dark_theme() -> str:
    """
    Get the dark theme stylesheet.
    
    Returns:
        str: CSS stylesheet content for the dark theme
    """
    css_content = get_theme_stylesheet("dark")
    
    # Fallback to embedded styles if CSS file is not available
    if not css_content.strip():
        return _get_fallback_dark_theme()
    
    return css_content


def _get_fallback_dark_theme() -> str:
    """
    Fallback dark theme in case CSS file is not available.
    
    Returns:
        str: Fallback CSS stylesheet content
    """
    return """
/* Fallback Dark Theme */
QWidget {
    color: #cdd6f4;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 11px;
}

QMainWindow {
    background-color: #181825;
}

.card {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 12px;
    padding: 16px;
    margin: 8px;
}

.file-drop {
    background-color: transparent;
    border: 2px dashed #6272a4;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    min-height: 80px;
    color: #f8f8f2;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7c3aed, stop:1 #6366f1);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    padding: 12px 12px;
    font-size: 12px;
}

QTextEdit {
    background-color: transparent;
    border: 1px solid #4b5563;
    border-radius: 8px;
    padding: 12px;
    color: #f3f4f6;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.4;
}

QLabel {
    color: #e5e7eb;
    font-weight: 500;
    font-size: 12px;
}
"""


# Main theme export - now loads from CSS file
DARK_THEME = get_dark_theme()
