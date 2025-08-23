# Installation Guide - TA Scheduler

## System Requirements

- **Python**: 3.12.6 or higher (recommended)
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended (Can be lower for smaller Datasets)
- **Storage**: 500MB free space (Can be lower for smaller Datasets)

## Quick Installation

### Option 1: Minimal Installation (Recommended for Users)

```bash
pip install -r requirements-minimal.txt
```

### Option 2: Full Installation (All Dependencies)

```bash
pip install -r requirements.txt
```

### Option 3: Development Installation (For Contributors)

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## Virtual Environment Setup (Recommended)

1. **Create virtual environment:**

   ```bash
   python -m venv ta_scheduler_env
   ```

2. **Activate environment:**

   - **Windows**: `ta_scheduler_env\Scripts\activate`
   - **macOS/Linux**: `source ta_scheduler_env/bin/activate`

3. **Install dependencies:**

   ```bash
   pip install -r requirements-minimal.txt
   ```

4. **Run application:**
   ```bash
   python main.py
   ```

## Dependency Overview

### Core Runtime Dependencies

- **pandas** (2.3.1+): Data processing and CSV handling
- **ortools** (9.14.6206+): Constraint programming optimization engine
- **PySide6** (6.9.1+): Modern Qt6-based GUI framework
- **openpyxl** (3.1.5+): Excel file generation with formatting

### Key Features Enabled by Dependencies

- **Constraint Programming**: Advanced TA assignment optimization using Google OR-Tools
- **Modern GUI**: Dark-themed desktop interface with drag-drop functionality
- **Excel Integration**: Interactive schedule generation with VBA automation
- **Data Processing**: Robust CSV parsing and DataFrame operations

## Troubleshooting

### Common Issues

1. **Import Error for PySide6**:

   - Ensure you have the latest pip: `pip install --upgrade pip`
   - Install PySide6 separately: `pip install PySide6>=6.9.1`

2. **OR-Tools Installation Issues**:

   - For older systems, try: `pip install ortools --no-cache-dir`
   - Check Python version compatibility

3. **Excel Generation Problems**:
   - Verify openpyxl installation: `python -c "import openpyxl; print(openpyxl.__version__)"`
   - Update to latest version: `pip install --upgrade openpyxl`

### Verification

Test your installation:

```bash
python -c "from src.gui.main_window import App; print('✅ Installation successful!')"
```

## Performance Notes

- The application uses constraint programming for optimization, which may take 1-5 minutes for large datasets (100+ TAs, 50+ lab slots)
- Excel generation is typically fast (<30 seconds) regardless of dataset size
- GUI responsiveness is maintained during long operations with progress indicators
