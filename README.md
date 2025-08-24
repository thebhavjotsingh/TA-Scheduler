# TA Scheduler

A modern desktop application for assigning Teaching Assistants (TAs) to lab sections using constraint programming optimization.

## Features

- **Modern GUI**: Clean, dark-themed interface with drag-and-drop file support
- **Smart Optimization**: Uses Google OR-Tools CP-SAT solver for efficient scheduling
- **Multiple Solutions**: Find up to 5 alternative optimal scheduling solutions for comparison
- **Comprehensive Reporting**: Detailed slot coverage and TA assignment summaries
- **Configurable Constraints**: Adjustable daily hour limits and min/max lab assignment ranges
- **CSV Integration**: Easy import/export of scheduling data
- **Partial Coverage**: Supports optimal partial slot filling when full coverage isn't possible

## Installation

### Quick Start (Recommended)

1. **Clone or download** this repository
2. **Install minimal dependencies**:
   ```bash
   pip install -r requirements-minimal.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### Full Installation Options

- **Minimal**: `pip install -r requirements-minimal.txt` (runtime only)
- **Complete**: `pip install -r requirements.txt` (includes all dependencies)
- **Development**: `pip install -r requirements.txt -r requirements-dev.txt` (for contributors)

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions and troubleshooting.

## Project Structure

```
TA Scheduler/appfiles/
├── main.py                    # Main application entry point
├── README.md                  # Project documentation
├── INSTALLATION.md            # Detailed installation guide
├── requirements.txt           # Complete Python dependencies with versions
├── requirements-minimal.txt   # Essential runtime dependencies only
├── requirements-dev.txt       # Additional development dependencies
├── TA Scheduler.spec         # Updated PyInstaller spec (now uses main.py)
├── CSS_STYLING_GUIDE.md      # Comprehensive CSS styling documentation
├── src/                      # Source code package
│   ├── __init__.py
│   ├── config/               # Configuration and constants
│   │   ├── __init__.py
│   │   ├── constants.py      # Application constants and file paths
│   │   ├── styles.py         # Theme management and CSS loading
│   │   ├── styles.css        # External CSS stylesheet (Qt-compatible)
│   │   └── stylesheet_loader.py # CSS file loading utilities
│   ├── core/                 # Core business logic
│   │   ├── __init__.py
│   │   ├── data_parser.py    # CSV parsing and validation functions
│   │   └── scheduler.py      # CP-SAT scheduling algorithm
│   ├── gui/                  # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   └── widgets.py        # Custom GUI widgets
│   └── utils/                # Utility functions
│       ├── __init__.py
│       └── time_utils.py     # Time conversion utilities
└── [existing files...]       # Original files preserved
```

## Usage

1. **Load CSV Files**: Drag and drop or browse for three required CSV files:

   - **Max Availability**: Contains TA names and hours hired
   - **Responses**: Contains TA unavailability data
   - **Requirements**: Contains lab section requirements

2. **Configure Constraints**: Set maximum daily hours and lab limits per TA

3. **Run Scheduler**: Click the run button to optimize assignments

4. **Export Results**: Optionally export detailed results to CSV files

## CSV File Formats

### Max Availability CSV

- **Columns**: `TA`, `Hired for`
- **Example**: Lists each TA and their total hired hours

### Responses CSV

- **Columns**: `Name`, `[1am to 2am ...]`, `[2am to 3am ...]`, etc.
- **Example**: Contains unavailability data for each time slot

### Requirements CSV

- **Columns**: `Day`, `Start`, `End`, `Required`, `Lab Section` (optional)
- **Example**: Defines when labs need TAs and how many

## Dependencies

- **Python 3.8+**
- **PySide6**: Modern Qt-based GUI framework
- **pandas**: Data manipulation and analysis
- **ortools**: Google's optimization tools (CP-SAT solver)

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller main.spec
```

## License

This project is open source. See the original file for any licensing terms.
