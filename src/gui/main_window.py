"""
Main application window for the TA Scheduler.
"""
import os
import sys
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QMessageBox, QSpinBox, QProgressBar, QScrollArea, QFrame, QGridLayout, 
    QFileDialog, QLineEdit
)
from PySide6.QtGui import QIcon, QFont, QTextCursor
from PySide6.QtCore import Qt, QTimer

from .widgets import ModernFileDropZone, ModernCard
from ..core.data_parser import parse_max_hours, parse_responses, parse_requirements
from ..core.scheduler import solve_schedule
from ..core.schedule_generator import generate_ta_schedule
from ..config.constants import (
    DEFAULT_APP_NAME, ICON_PATH, MAX_DAILY_HOURS, MAX_LABS_PER_TA, 
    SLOT_OUTPUT_CSV, TA_OUTPUT_CSV
)
from ..config.styles import DARK_THEME


class App(QWidget):
    """
    Modern, responsive main application window with dark theme and card-based design.
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """Initialize the modern UI with card-based layout"""
        self.setWindowTitle(f"{DEFAULT_APP_NAME}")
        if os.path.exists(ICON_PATH):
            # Create high-quality icon with multiple sizes
            icon = QIcon(ICON_PATH)
            # Ensure the icon is treated as high DPI
            icon.setIsMask(False)
            self.setWindowIcon(icon)
        
        # Set minimum size and make responsive
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
        
        # Main layout with padding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.create_header(main_layout)
        
        # Create scroll area for responsive design
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        
        # Content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # File input section
        self.create_file_input_section(content_layout)
        
        # Configuration section
        self.create_configuration_section(content_layout)
        
        # Results section
        self.create_results_section(content_layout)
        
        # Add content to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_header(self, layout):
        """Create the modern header section with integrated action button"""
        header_card = ModernCard()
        header_main_layout = QVBoxLayout()
        
        # Row 1: Title and status
        title_row = QHBoxLayout()
        
        title_label = QLabel("TA Scheduler")
        title_label.setProperty("class", "section-title")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        # Status indicator
        status_label = QLabel("🟢 Ready")
        status_label.setProperty("class", "status")
        title_row.addWidget(status_label)
        
        # Add title row to main layout
        header_main_layout.addLayout(title_row)
        
        # Row 2: Subtitle (left) and Run Button (right)
        subtitle_button_row = QHBoxLayout()
        
        subtitle_label = QLabel("Intelligent constraint-based scheduling with CP-SAT optimization")
        subtitle_label.setProperty("class", "subtitle")
        subtitle_button_row.addWidget(subtitle_label)
        subtitle_button_row.addStretch()
        
        # Main action button - right aligned
        self.run_button = QPushButton("Run Scheduler")
        self.run_button.clicked.connect(self.run)
        self.run_button.setMinimumHeight(25)
        # Remove max width to allow dynamic sizing based on text content
        self.run_button.setMinimumWidth(100)  # Ensure minimum readability
        self.run_button.setProperty("class", "primary")
        subtitle_button_row.addWidget(self.run_button)
        
        header_main_layout.addLayout(subtitle_button_row)
        
        # Row 3: Progress bar (centered)
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Optimizing schedule... %p%")
        self.progress_bar.setMaximumWidth(200)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        
        header_main_layout.addLayout(progress_layout)
        
        header_card.add_layout(header_main_layout)
        layout.addWidget(header_card)

    def create_file_input_section(self, layout):
        """Create the file input section with modern drop zones"""
        files_card = ModernCard("📁 Input Files")
        
        # Grid layout for responsive file inputs
        files_grid = QGridLayout()
        files_grid.setSpacing(8)
        
        # Create modern file drop zones
        self.max_drop_zone = ModernFileDropZone(
            "Max Availability CSV",
            "Columns: TA, Hired for"
        )
        
        self.resp_drop_zone = ModernFileDropZone(
            "Responses CSV", 
            "Columns: Name + Unavailability[...] columns"
        )
        
        self.req_drop_zone = ModernFileDropZone(
            "Requirements CSV",
            "Columns: Day, Start, End, Required"
        )
        
        # Add to grid (responsive: 1 column on small, 3 on large)
        files_grid.addWidget(self.max_drop_zone, 0, 0)
        files_grid.addWidget(self.resp_drop_zone, 0, 1)
        files_grid.addWidget(self.req_drop_zone, 0, 2)
        
        files_card.add_layout(files_grid)
        layout.addWidget(files_card)

    def create_configuration_section(self, layout):
        """Create the configuration section with modern controls"""
        config_card = ModernCard("⚙️ Scheduling Constraints")
        
        config_layout = QHBoxLayout()
        config_layout.setSpacing(24)
        config_layout.addStretch()  # Add stretch before content to center it
        
        # Max daily hours control
        daily_group = QVBoxLayout()
        daily_group.setAlignment(Qt.AlignCenter)  # Center align the group
        daily_label = QLabel("Max Daily Hours")
        daily_label.setProperty("class", "control-label")
        daily_label.setAlignment(Qt.AlignCenter)  # Center align the label
        
        self.daily_hours_input = QLineEdit()
        self.daily_hours_input.setText(str(MAX_DAILY_HOURS))
        self.daily_hours_input.setToolTip("Maximum hours a TA can work in a single day")
        self.daily_hours_input.setMinimumWidth(80)
        self.daily_hours_input.setMaximumWidth(120)
        self.daily_hours_input.setAlignment(Qt.AlignCenter)  # Center align the text
        self.daily_hours_input.setPlaceholderText("e.g., 8")
        
        daily_hint = QLabel("Hours per day limit")
        daily_hint.setProperty("class", "hint")
        daily_hint.setAlignment(Qt.AlignCenter)  # Center align the hint
        
        daily_group.addWidget(daily_label)
        daily_group.addWidget(self.daily_hours_input)
        daily_group.addWidget(daily_hint)
        
        # Max labs control
        labs_group = QVBoxLayout()
        labs_group.setAlignment(Qt.AlignCenter)  # Center align the group
        labs_label = QLabel("Max Labs per TA")
        labs_label.setProperty("class", "control-label")
        labs_label.setAlignment(Qt.AlignCenter)  # Center align the label
        
        self.max_labs_input = QLineEdit()
        self.max_labs_input.setText(str(MAX_LABS_PER_TA))
        self.max_labs_input.setToolTip("Maximum number of different labs a TA can be assigned to")
        self.max_labs_input.setMinimumWidth(80)
        self.max_labs_input.setMaximumWidth(120)
        self.max_labs_input.setAlignment(Qt.AlignCenter)  # Center align the text
        self.max_labs_input.setPlaceholderText("e.g., 3")
        
        labs_hint = QLabel("Lab assignment limit")
        labs_hint.setProperty("class", "hint")
        labs_hint.setAlignment(Qt.AlignCenter)  # Center align the hint
        
        labs_group.addWidget(labs_label)
        labs_group.addWidget(self.max_labs_input)
        labs_group.addWidget(labs_hint)
        
        config_layout.addLayout(daily_group)
        config_layout.addLayout(labs_group)
        config_layout.addStretch()
        
        config_card.add_layout(config_layout)
        
        # Add the card with full width but centered content
        layout.addWidget(config_card)

    def create_results_section(self, layout):
        """Create the results section with modern log output"""
        results_card = ModernCard("📊 Results & Logs")
        
        # Log output area with modern styling - responsive height
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(150)
        self.log_area.setPlaceholderText("Results will appear here after running the scheduler...")
        
        # Force content to stay at top-left
        self.log_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Ensure text starts from top-left always
        cursor = self.log_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.log_area.setTextCursor(cursor)
        
        results_card.add_widget(self.log_area)
        layout.addWidget(results_card)

    def setup_animations(self):
        """Setup hover animations and effects"""
        # Animation can be added here for button hover effects, etc.
        pass

    def create_wide_message_box(self, icon, title, text, buttons=None):
        """Create a message box with wider buttons"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        # Apply custom styling to make buttons wider
        msg_box.setStyleSheet("""
            QMessageBox QPushButton {
                min-width: 30px;
                padding: 3px 10px;
                font-size: 11px;
            }
        """)
        
        if buttons:
            for button_text, button_role in buttons:
                msg_box.addButton(button_text, button_role)
        
        return msg_box

    def show_progress(self):
        """Show progress bar with animation"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.run_button.setEnabled(False)
        self.run_button.setText("⏳ Processing...")

    def hide_progress(self):
        """Hide progress bar and restore button"""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Scheduler")

    def update_button_text(self, text):
        """Update button text and let it resize dynamically"""
        self.run_button.setText(text)
        # Force button to recalculate its size
        self.run_button.updateGeometry()

    def log(self, message: str):
        """
        Append a message to the log output area with color coding.
        """
        # Add some basic color coding for different message types
        if "✓" in message or "FULLY COVERED" in message:
            colored_message = f'<span style="color: #10b981;">{message}</span>'
        elif "⚠" in message or "PARTIALLY FILLED" in message:
            colored_message = f'<span style="color: #f59e0b;">{message}</span>'
        elif "✗" in message or "UNFILLED" in message or "Error" in message:
            colored_message = f'<span style="color: #ef4444;">{message}</span>'
        elif "SUMMARY:" in message:
            colored_message = f'<span style="color: #8b5cf6; font-weight: bold;">{message}</span>'
        else:
            colored_message = message
        
        self.log_area.append(colored_message)
        
        # Ensure the text area starts from top when first content is added
        if self.log_area.document().blockCount() <= 2:  # First few messages
            cursor = self.log_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.log_area.setTextCursor(cursor)
            self.log_area.ensureCursorVisible()

    def run(self):
        """
        Main entrypoint when 'Run Scheduler' is clicked:
          1) Validate CSV inputs from modern drop zones
          2) Parse data
          3) Solve scheduling using Constraint Programming
          4) Display results and optionally export
        """
        # Get file paths from modern drop zones
        max_path = self.max_drop_zone.get_file_path()
        resp_path = self.resp_drop_zone.get_file_path()
        req_path = self.req_drop_zone.get_file_path()

        # Validate selected file paths
        if not (max_path and max_path.endswith('.csv') and os.path.exists(max_path)):
            msg_box = self.create_wide_message_box(
                QMessageBox.Warning, 
                DEFAULT_APP_NAME, 
                "Please select a valid Max Availability CSV file."
            )
            msg_box.exec()
            return
        if not (resp_path and resp_path.endswith('.csv') and os.path.exists(resp_path)):
            msg_box = self.create_wide_message_box(
                QMessageBox.Warning, 
                DEFAULT_APP_NAME, 
                "Please select a valid Responses CSV file."
            )
            msg_box.exec()
            return
        if not (req_path and req_path.endswith('.csv') and os.path.exists(req_path)):
            msg_box = self.create_wide_message_box(
                QMessageBox.Warning, 
                DEFAULT_APP_NAME, 
                "Please select a valid Requirements CSV file."
            )
            msg_box.exec()
            return

        # Show progress and clear log
        self.show_progress()
        self.log_area.clear()
        
        # Simulate progress updates
        progress_timer = QTimer()
        progress_value = 0
        
        def update_progress():
            nonlocal progress_value
            progress_value += 10
            self.progress_bar.setValue(min(progress_value, 90))
            if progress_value >= 90:
                progress_timer.stop()
        
        progress_timer.timeout.connect(update_progress)
        progress_timer.start(100)
        
        try:
            # Parse input CSVs
            self.log("🔄 Loading and parsing CSV files...")
            emps, maxh = parse_max_hours(max_path)
            responses_df = pd.read_csv(resp_path)
            slots = parse_requirements(req_path)
            
            # Check for missing availability submissions
            availability, missing_tas = parse_responses(resp_path, emps)
            
            if missing_tas:
                self.log("")
                self.log("⚠️ MISSING AVAILABILITY SUBMISSIONS:")
                self.log("=" * 40)
                for ta in missing_tas:
                    self.log(f"❌ {ta} - No availability submitted")
                self.log(f"📊 Total missing: {len(missing_tas)} out of {len(emps)} TAs")
                self.log("")
            
            if not slots:
                raise ValueError('No slots to schedule. Please check your Requirements CSV file.')
                
            self.log(f"✅ Loaded {len(emps)} TAs, {len(slots)} slots")
            self.log("🧠 Using Constraint Programming (CP-SAT) optimization...")
            self.log("")
            
            # Get constraint values from GUI with validation
            try:
                max_daily_hours = int(self.daily_hours_input.text().strip())
                if max_daily_hours <= 0:
                    raise ValueError("Max daily hours must be positive")
            except ValueError:
                msg_box = self.create_wide_message_box(
                    QMessageBox.Warning, 
                    "Invalid Input", 
                    "Please enter a valid positive number for Max Daily Hours"
                )
                msg_box.exec()
                return
            
            try:
                max_labs_per_ta = int(self.max_labs_input.text().strip())
                if max_labs_per_ta <= 0:
                    raise ValueError("Max labs per TA must be positive")
            except ValueError:
                msg_box = self.create_wide_message_box(
                    QMessageBox.Warning, 
                    "Invalid Input", 
                    "Please enter a valid positive number for Max Labs per TA"
                )
                msg_box.exec()
                return
            
            self.log(f"⚙️ Constraints: {max_daily_hours}h/day max, {max_labs_per_ta} labs/TA max")
            self.log("")
                
            # Solve the scheduling problem
            self.progress_bar.setValue(95)
            slot_res, ta_res = solve_schedule(emps, responses_df, maxh, slots, 
                                            max_daily_hours, max_labs_per_ta, self.log)

            self.progress_bar.setValue(100)
            self.log("")
            self.log("📋 DETAILED RESULTS:")
            self.log("=" * 50)

            # Display slot assignment summary with enhanced formatting
            for s in slot_res:
                section = s['Lab Section'] if s['Lab Section'] else f"Slot {slot_res.index(s)}"
                assigned_count = s['Assigned Count']
                required_count = s['Required Count']
                time_info = f"({s['Day']} {s['Start Time']}-{s['End Time']})"
                
                if s['TAs Assigned'] and s['Needed'] == 0:
                    self.log(f"✅ {section} {time_info}: FULLY COVERED - {s['TAs Assigned']} ({assigned_count}/{required_count})")
                elif s['TAs Assigned']:
                    self.log(f"⚠️ {section} {time_info}: PARTIALLY FILLED - {s['TAs Assigned']} ({assigned_count}/{required_count}, need {s['Needed']} more)")
                else:
                    self.log(f"❌ {section} {time_info}: UNFILLED - Need {s['Needed']} TAs ({assigned_count}/{required_count})")
            
            self.log("")

            # Enhanced summary statistics
            fully_covered = sum(1 for s in slot_res if s['Needed'] == 0)
            partially_filled = sum(1 for s in slot_res if s['Assigned Count'] > 0 and s['Needed'] > 0)
            unfilled = sum(1 for s in slot_res if s['Assigned Count'] == 0)
            total_slots = len(slot_res)
            
            coverage_percent = (fully_covered / total_slots * 100) if total_slots > 0 else 0
            
            self.log("📊 SUMMARY STATISTICS:")
            self.log(f"   🟢 Fully Covered: {fully_covered} slots ({coverage_percent:.1f}%)")
            self.log(f"   🟡 Partially Filled: {partially_filled} slots")
            self.log(f"   🔴 Unfilled: {unfilled} slots")
            self.log(f"   📈 Total Slots: {total_slots}")
            self.log("")

            # Display TA assignments with better formatting
            self.log("👥 TA ASSIGNMENTS:")
            for t in ta_res:
                daily_info = f" ({t['Daily Breakdown']})" if t['Daily Breakdown'] != "None" else ""
                labs_info = f" - Labs: {t['Labs Assigned']}" if t['Labs Assigned'] != "None" else ""
                utilization = f"{t['Hours Assigned']}/{t['Hours Hired For']}"
                self.log(f"   • {t['TA Name']}: {utilization}h assigned{daily_info}{labs_info}")

            # Complete progress
            progress_timer.stop()
            self.progress_bar.setValue(100)
            QTimer.singleShot(1000, self.hide_progress)

            # Enhanced export dialog
            msg_box = self.create_wide_message_box(
                QMessageBox.Question,
                f"Export Results – {DEFAULT_APP_NAME}",
                "🎯 Optimization complete! Would you like to export the results to CSV files?"
            )
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            reply = msg_box.exec()
            
            if reply == QMessageBox.Yes:
                dir_path = QFileDialog.getExistingDirectory(
                    self, "Select export directory", os.getcwd(), QFileDialog.ShowDirsOnly
                )
                if dir_path:
                    # Clean up and export data
                    slot_df = pd.DataFrame(slot_res).fillna('')
                    ta_df = pd.DataFrame(ta_res).fillna('')
                    
                    slot_df.to_csv(os.path.join(dir_path, SLOT_OUTPUT_CSV), index=False)
                    ta_df.to_csv(os.path.join(dir_path, TA_OUTPUT_CSV), index=False)
                    self.log(f"\n💾 CSV files exported to: {dir_path}")
                    
                    # Offer Excel schedule generation
                    self.show_excel_generation_dialog(dir_path, ta_df, responses_df)
                else:
                    self.log("\n❌ Export canceled: no directory selected.")
            else:
                self.log("\n⏭️ CSV export skipped.")
                # Still offer Excel generation
                ta_df = pd.DataFrame(ta_res).fillna('')
                self.show_excel_generation_dialog(None, ta_df, responses_df)

        except Exception as e:
            # Enhanced error handling
            progress_timer.stop()
            self.hide_progress()
            
            import traceback
            
            # Create modern error dialog
            error_msg = QMessageBox(self)
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setWindowTitle(f"Error - {DEFAULT_APP_NAME}")
            error_msg.setText("❌ An error occurred during execution:")
            
            # Apply wide button styling
            error_msg.setStyleSheet("""
                QMessageBox QPushButton {
                    min-width: 30px;
                    padding: 3px 10px;
                    font-weight: bold;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                    background-color: #f8f9fa;
                }
                QMessageBox QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
            
            # Include full traceback for debugging
            full_error = f"{str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
            error_msg.setDetailedText(full_error)
            
            # Add custom buttons
            try_again_btn = error_msg.addButton("🔄 Try Again", QMessageBox.ActionRole)
            exit_btn = error_msg.addButton("🚪 Exit App", QMessageBox.DestructiveRole)
            
            error_msg.setModal(True)
            result = error_msg.exec()
            
            if error_msg.clickedButton() == exit_btn:
                sys.exit(1)
            
            # Log error in the UI as well
            self.log(f"❌ Error: {str(e)}")
            self.log("Please check your CSV files and try again.")

    def show_excel_generation_dialog(self, default_dir, ta_df, responses_df):
        """Show dialog for Excel schedule generation"""
        msg_box = self.create_wide_message_box(
            QMessageBox.Question,
            f"Generate Excel Schedule – {DEFAULT_APP_NAME}",
            "📊 Would you like to generate an interactive Excel schedule mapping?\n\n"
            "This will create an Excel file with:\n"
            "• Individual TA schedule sheets\n"
            "• Office Hours tracking\n"
            "• VBA code for real-time updates"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = msg_box.exec()
        
        if reply == QMessageBox.Yes:
            # Select directory for Excel export
            if default_dir:
                excel_dir = default_dir
            else:
                excel_dir = QFileDialog.getExistingDirectory(
                    self, "Select directory for Excel schedule", os.getcwd(), QFileDialog.ShowDirsOnly
                )
            
            if excel_dir:
                try:
                    self.log(f"\n📊 Generating Excel schedule mapping...")
                    
                    # Generate the Excel schedule using DataFrames directly (no temp files needed)
                    excel_file, vba_module_file, vba_thisworkbook_file = generate_ta_schedule(
                        ta_df, responses_df, excel_dir
                    )
                    
                    self.log(f"✅ Excel file created: {os.path.basename(excel_file)}")
                    self.log(f"📋 VBA code files created for manual installation:")
                    self.log(f"   • {os.path.basename(vba_module_file)}")
                    self.log(f"   • {os.path.basename(vba_thisworkbook_file)}")
                    self.log(f"\n💡 To enable real-time Office Hours updates:")
                    self.log(f"   1. Open the Excel file")
                    self.log(f"   2. Press Alt/Option+F11 to open VBA editor")
                    self.log(f"   3. Insert > Module, paste code from vba_module_code.txt")
                    self.log(f"   4. Double-click 'ThisWorkbook', paste code from vba_thisworkbook_code.txt")
                    self.log(f"   5. Save as .xlsm (Excel Macro-Enabled Workbook)")
                    
                    # Show completion message
                    completion_msg = self.create_wide_message_box(
                        QMessageBox.Information,
                        "Excel Schedule Generated",
                        f"Excel schedule mapping successfully created!\n\n"
                        f"Location: {excel_dir}\n"
                        f"File: {os.path.basename(excel_file)}\n\n"
                        f"VBA files for dynamic updates are also included."
                        f"⚠️ Refer Instructions in the log for enabling VBA macros"
                    )
                    completion_msg.setStandardButtons(QMessageBox.Ok)
                    completion_msg.exec()
                    
                except Exception as e:
                    self.log(f"\n❌ Error generating Excel schedule: {str(e)}")
                    error_msg = self.create_wide_message_box(
                        QMessageBox.Critical,
                        "Excel Generation Error",
                        f"Failed to generate Excel schedule:\n\n{str(e)}"
                    )
                    error_msg.setStandardButtons(QMessageBox.Ok)
                    error_msg.exec()
            else:
                self.log("\n❌ Excel generation canceled: no directory selected.")
        else:
            self.log("\n⏭️ Excel schedule generation skipped.")
