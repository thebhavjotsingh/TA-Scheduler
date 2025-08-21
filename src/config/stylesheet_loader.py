"""
Stylesheet utilities for loading and managing CSS files.
"""
import os


def load_stylesheet(css_filename: str) -> str:
    """
    Load a CSS stylesheet from the config directory.
    
    Args:
        css_filename (str): Name of the CSS file to load
        
    Returns:
        str: CSS content as a string, or empty string if file not found
    """
    try:
        # Get the directory where this file is located (config directory)
        config_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(config_dir, css_filename)
        
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"Warning: CSS file '{css_filename}' not found at {css_path}")
            return ""
    except Exception as e:
        print(f"Error loading CSS file '{css_filename}': {e}")
        return ""


def get_theme_stylesheet(theme_name: str = "dark") -> str:
    """
    Get the stylesheet for a specific theme.
    
    Args:
        theme_name (str): Name of the theme ('dark', 'light', etc.)
        
    Returns:
        str: CSS stylesheet content
    """
    css_filename = f"styles.css"
    return load_stylesheet(css_filename)


def combine_stylesheets(*css_files: str) -> str:
    """
    Combine multiple CSS files into a single stylesheet.
    
    Args:
        *css_files: Variable number of CSS filenames to combine
        
    Returns:
        str: Combined CSS content
    """
    combined_css = []
    for css_file in css_files:
        css_content = load_stylesheet(css_file)
        if css_content:
            combined_css.append(f"/* From {css_file} */")
            combined_css.append(css_content)
            combined_css.append("")  # Add spacing between files
    
    return "\n".join(combined_css)
