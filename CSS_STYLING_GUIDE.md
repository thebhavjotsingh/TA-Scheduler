# CSS Styling System Documentation

## Overview

The TA Scheduler now uses an external CSS stylesheet for better maintainability and easier theme management. This system provides separation between styling and application logic.

## Architecture

### 📁 File Structure

```
src/config/
├── styles.css           # Main Qt-compatible CSS stylesheet
├── styles.py           # Python stylesheet loader and theme management
├── stylesheet_loader.py # Utility functions for CSS loading
└── constants.py        # Application constants
```

### 🔄 How It Works

1. **CSS File**: `styles.css` contains all Qt-compatible styling rules
2. **Loader**: `stylesheet_loader.py` loads and processes CSS files
3. **Theme Manager**: `styles.py` provides theme functions and fallback styles
4. **Application**: Main application loads the theme via `DARK_THEME` import

## CSS Classes and Selectors

### 🏷️ Widget Classes

The following CSS classes are available for styling widgets:

#### Buttons

- `QPushButton[class="primary"]` - Main action buttons (Run Scheduler)
- `QPushButton[class="secondary"]` - Secondary action buttons
- `QPushButton` - Default button styling

#### Labels

- `QLabel[class="section-title"]` - Main section headings (24px, bold)
- `QLabel[class="card-title"]` - Card section titles (14px, semibold)
- `QLabel[class="subtitle"]` - Descriptive text (13px, muted)
- `QLabel[class="hint"]` - Helper text (10px, subtle)
- `QLabel[class="control-label"]` - Form control labels (12px, semibold)
- `QLabel[class="status"]` - Status indicators (green color)

#### File Drop Zone Labels

- `QLabel[class="file-icon"]` - File icons (32px)
- `QLabel[class="file-title"]` - File drop zone titles
- `QLabel[class="file-subtitle"]` - File drop zone descriptions
- `QLabel[class="file-path"]` - File path display

#### Containers

- `QFrame[class="card"]` - Card containers with shadows and borders
- `QFrame[class="file-drop-success"]` - Success state for file drops

### 🎨 Color Scheme

The dark theme uses the following color palette:

```css
/* Primary Colors */
Background: #181825    /* Main window background */
Cards: #313244         /* Card backgrounds */
Borders: #45475a       /* Default borders */
Text: #cdd6f4          /* Primary text */
Muted: #9ca3af         /* Secondary text */

/* Accent Colors */
Primary: #7c3aed       /* Primary buttons and accents */
Success: #10b981       /* Success states */
Warning: #f59e0b       /* Warning states */
Error: #ef4444         /* Error states */
Info: #06b6d4          /* Info states */
```

## Usage Examples

### 🔨 Applying CSS Classes in Python

```python
# Primary button
button = QPushButton("Run Scheduler")
button.setProperty("class", "primary")

# Section title
title = QLabel("TA Scheduler")
title.setProperty("class", "section-title")

# Card container
card = QFrame()
card.setProperty("class", "card")

# Status label
status = QLabel("🟢 Ready")
status.setProperty("class", "status")
```

### 🎭 Dynamic Class Changes

```python
# Change file icon to success state
self.icon_label.setProperty("class", "file-icon success")

# Update widget styling after class change
widget.style().unpolish(widget)
widget.style().polish(widget)
```

## CSS Loading System

### 📥 Automatic Loading

The CSS is automatically loaded when importing `DARK_THEME`:

```python
from src.config.styles import DARK_THEME
app.setStyleSheet(DARK_THEME)
```

### 🔄 Fallback System

If the CSS file is missing or corrupted, the system automatically falls back to embedded styles:

```python
def get_dark_theme() -> str:
    css_content = get_theme_stylesheet("dark")

    # Fallback to embedded styles if CSS file is not available
    if not css_content.strip():
        return _get_fallback_dark_theme()

    return css_content
```

### 🧩 Multiple CSS Files

The system supports combining multiple CSS files:

```python
from src.config.stylesheet_loader import combine_stylesheets

combined = combine_stylesheets("base.css", "theme.css", "components.css")
```

## Qt CSS Compatibility

### ✅ Supported Features

- Widget selectors (`QPushButton`, `QLabel`, etc.)
- Attribute selectors (`[class="primary"]`)
- Pseudo-states (`:hover`, `:pressed`, `:focus`)
- Sub-controls (`::chunk`, `::handle`)
- Color values (hex, rgba)
- Gradients (`qlineargradient`)
- Border radius and padding

### ❌ Limitations

- No CSS animations (use Qt animations instead)
- Limited box model support
- No flexbox or grid layouts
- No media queries (responsive design via Qt layout system)
- No CSS variables (use Python constants instead)

## Customization Guide

### 🎨 Adding New Themes

1. Create a new CSS file (e.g., `light-theme.css`)
2. Add a loader function in `styles.py`:
   ```python
   def get_light_theme() -> str:
       return get_theme_stylesheet("light")
   ```
3. Update theme selection logic

### 🧩 Adding New Components

1. Define CSS classes in `styles.css`:
   ```css
   QWidget[class="my-component"] {
     background: #313244;
     border-radius: 8px;
   }
   ```
2. Apply classes in Python widgets:
   ```python
   widget.setProperty("class", "my-component")
   ```

### 🎯 Modifying Existing Styles

1. Edit `styles.css` directly
2. Restart the application to see changes
3. Consider adding fallback styles in `styles.py`

## Benefits

### 🎯 **Maintainability**

- ✅ Centralized styling in CSS files
- ✅ Separation of concerns (styling vs. logic)
- ✅ Easy to find and modify styles
- ✅ Version control friendly

### 🚀 **Development Experience**

- ✅ Hot-reload during development (restart app)
- ✅ Familiar CSS syntax for web developers
- ✅ Better tooling support (CSS syntax highlighting)
- ✅ Fallback system prevents crashes

### 🔧 **Flexibility**

- ✅ Multiple theme support
- ✅ Component-based styling system
- ✅ Easy customization and extension
- ✅ Qt-specific features supported

## Troubleshooting

### 🐛 Common Issues

1. **"Could not parse application stylesheet"**

   - Check CSS syntax for Qt compatibility
   - Ensure proper selector format
   - Verify file encoding is UTF-8

2. **Styles not applying**

   - Verify CSS class is properly set with `setProperty("class", "name")`
   - Call `style().unpolish()` and `style().polish()` after class changes
   - Check CSS selector specificity

3. **CSS file not found**
   - Verify file path in `stylesheet_loader.py`
   - Check file permissions
   - System will use fallback styles automatically

### 🔍 Debugging Tips

- Use Python's CSS loading functions to test stylesheet loading
- Check Qt documentation for supported CSS features
- Test individual selectors in isolation
- Use Qt Inspector tools for widget hierarchy analysis

This CSS system provides a robust, maintainable foundation for the TA Scheduler's visual design while maintaining Qt compatibility and providing graceful fallbacks.
