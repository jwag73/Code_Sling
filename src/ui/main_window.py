# src/ui/main_window.py

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QDialog, QDialogButtonBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QClipboard

# --- Core Logic Imports ---
from src.ai.reasoning_agent import ReasoningAgent # Assumes this can take settings
from src.core.parser import parse_instructions, ParsedInstruction
from src.core.injector import apply_instructions

# --- Logging Imports ---
import time
import json
from pathlib import Path
import re
import uuid
import dataclasses # For asdict
import traceback # For detailed error logging

# Placeholder texts
PLACEHOLDER_ORIGINAL_CODE = "Paste your original code here...\n\n# Example:\ndef hello_world():\n    print(\"Hello, Original World!\")"
PLACEHOLDER_AI_SUGGESTION = "Paste AI's suggested code or instructions here...\n\n# Example:\n# Replace the print statement in hello_world with:\n# print(\"Hello, AI Enhanced World!\")"
PLACEHOLDER_MODIFIED_CODE = "Modified code will appear here..."

class CodeEditorDialog(QDialog):
    def __init__(self, parent=None, window_title="Edit Code", initial_text=""):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setMinimumSize(600, 400)
        self.layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.layout.addWidget(self.text_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
    def get_text(self):
        return self.text_edit.toPlainText()


class MainWindow(QMainWindow):
    def __init__(self, settings): # Requires settings object
        super().__init__()
        self.settings = settings

        # Recommendation: Pass settings to ReasoningAgent
        # This assumes ReasoningAgent.__init__ is modified to accept settings
        self.reasoning_agent = ReasoningAgent(settings=self.settings)

        self.setWindowTitle("Code_Slinge V1.0 (MVP)")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)

        self.session_log_filepath = None
        self.current_session_id = None
        self.last_processed_event_id = None # For linking feedback
        self._setup_session_logging()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_widgets()
        self._setup_layouts()
        self._connect_signals()

    def _setup_session_logging(self):
        # Recommendation: Harden settings access
        default_data_path = Path("data") # Define a default path
        base_log_dir_str = getattr(self.settings, 'data_dir', default_data_path.as_posix())
        base_log_dir = Path(base_log_dir_str) # Ensure it's a Path object
        log_dir = base_log_dir / "code_sling_sessions"
        # If you preferred "Historical data" and it wasn't settings-driven:
        # log_dir = Path("Historical data")

        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"CRITICAL ERROR: Could not create log directory {log_dir}: {e}. Logging will be disabled.")
            self.session_log_filepath = None # Ensure logging is disabled
            return

        max_session_num = 0
        session_file_pattern = re.compile(r"session_(\d+)\.jsonl")
        for f_path in log_dir.glob("session_*.jsonl"):
            match = session_file_pattern.match(f_path.name)
            if match:
                try:
                    max_session_num = max(max_session_num, int(match.group(1)))
                except ValueError:
                    print(f"Warning: Could not parse session number from filename: {f_path.name}")

        self.current_session_id = max_session_num + 1
        self.session_log_filepath = log_dir / f"session_{self.current_session_id}.jsonl"
        print(f"INFO: Logging current session (ID: {self.current_session_id}) to: {self.session_log_filepath}")

        # Recommendation: Harden settings access for metadata
        model_name_for_meta = getattr(self.settings, "openai_model", "N/A")
        timeout_for_meta = getattr(self.settings, "timeout_seconds", "N/A") # Ensure this is a string if N/A

        session_meta_entry = {
            "timestamp_unix": time.time(),
            "session_id": self.current_session_id,
            "event_type": "session_start_metadata",
            "settings_snapshot": {
                "openai_model": str(model_name_for_meta), # Ensure string
                "timeout_seconds": str(timeout_for_meta), # Ensure string
            }
        }
        try:
            with open(self.session_log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(session_meta_entry) + '\n')
        except Exception as e:
            print(f"ERROR: Could not write session metadata to log file {self.session_log_filepath}: {e}")
            # Potentially disable further logging or handle more gracefully
            # self.session_log_filepath = None


    def _create_widgets(self):
        self.btn_expand_original = QPushButton("Expand Original Code View")
        self.btn_expand_ai_suggestion = QPushButton("Expand AI Suggestion View")
        self.txt_original_code = QTextEdit()
        self.txt_original_code.setPlaceholderText(PLACEHOLDER_ORIGINAL_CODE)
        self.btn_clear_original = QPushButton("Clear")
        self.btn_copy_original = QPushButton("Copy")
        self.txt_ai_suggestion = QTextEdit()
        self.txt_ai_suggestion.setPlaceholderText(PLACEHOLDER_AI_SUGGESTION)
        self.btn_clear_ai_suggestion = QPushButton("Clear")
        self.btn_copy_ai_suggestion = QPushButton("Copy")
        self.btn_process_code = QPushButton(">>> PROCESS CODE <<<")
        font = self.btn_process_code.font()
        font.setPointSize(14); font.setBold(True); self.btn_process_code.setFont(font)
        self.btn_process_code.setFixedHeight(50)
        self.btn_expand_output = QPushButton("Expand Output Code View")
        self.txt_modified_code = QTextEdit()
        self.txt_modified_code.setPlaceholderText(PLACEHOLDER_MODIFIED_CODE)
        self.txt_modified_code.setReadOnly(False) # Allow editing of output
        self.btn_clear_output = QPushButton("Clear")
        self.btn_copy_output = QPushButton("Copy")

        self.btn_ai_did_good = QPushButton("👍 AI Outcome Good")
        self.btn_ai_did_bad = QPushButton("👎 AI Outcome Bad")

        # Recommendation: Optional - mutate the feedback buttons’ setEnabled
        self.btn_ai_did_good.setEnabled(False) # Start disabled
        self.btn_ai_did_bad.setEnabled(False)  # Start disabled

    def _setup_layouts(self):
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addWidget(self.btn_expand_original)
        top_buttons_layout.addWidget(self.btn_expand_ai_suggestion)
        self.main_layout.addLayout(top_buttons_layout)

        inputs_layout = QHBoxLayout()
        original_code_layout = QVBoxLayout()
        original_code_layout.addWidget(self.txt_original_code)
        original_code_buttons_layout = QHBoxLayout()
        original_code_buttons_layout.addWidget(self.btn_clear_original)
        original_code_buttons_layout.addWidget(self.btn_copy_original)
        original_code_buttons_layout.addStretch()
        original_code_layout.addLayout(original_code_buttons_layout)
        inputs_layout.addLayout(original_code_layout)

        ai_suggestion_layout = QVBoxLayout()
        ai_suggestion_layout.addWidget(self.txt_ai_suggestion)
        ai_suggestion_buttons_layout = QHBoxLayout()
        ai_suggestion_buttons_layout.addWidget(self.btn_clear_ai_suggestion)
        ai_suggestion_buttons_layout.addWidget(self.btn_copy_ai_suggestion)
        ai_suggestion_buttons_layout.addStretch()
        ai_suggestion_layout.addLayout(ai_suggestion_buttons_layout)
        inputs_layout.addLayout(ai_suggestion_layout)
        self.main_layout.addLayout(inputs_layout)

        self.main_layout.addWidget(self.btn_process_code, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.btn_expand_output)
        output_layout = QVBoxLayout()
        output_layout.addWidget(self.txt_modified_code)
        output_buttons_layout = QHBoxLayout()
        output_buttons_layout.addWidget(self.btn_clear_output)
        output_buttons_layout.addWidget(self.btn_copy_output)
        output_buttons_layout.addStretch()
        output_layout.addLayout(output_buttons_layout)
        self.main_layout.addLayout(output_layout)

        self.txt_original_code.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.txt_ai_suggestion.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.txt_modified_code.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()
        bottom_buttons_layout.addWidget(self.btn_ai_did_good)
        bottom_buttons_layout.addWidget(self.btn_ai_did_bad)
        bottom_buttons_layout.addStretch()
        self.main_layout.addLayout(bottom_buttons_layout)


    def _connect_signals(self):
        self.btn_expand_original.clicked.connect(lambda: self._open_editor_dialog(self.txt_original_code, "Original Code"))
        self.btn_expand_ai_suggestion.clicked.connect(lambda: self._open_editor_dialog(self.txt_ai_suggestion, "AI Suggestion"))
        self.btn_expand_output.clicked.connect(lambda: self._open_editor_dialog(self.txt_modified_code, "Modified Code Output"))
        self.btn_clear_original.clicked.connect(lambda: self.txt_original_code.clear())
        self.btn_clear_ai_suggestion.clicked.connect(lambda: self.txt_ai_suggestion.clear())
        self.btn_clear_output.clicked.connect(lambda: self.txt_modified_code.clear())
        self.btn_copy_original.clicked.connect(lambda: self._copy_to_clipboard(self.txt_original_code.toPlainText()))
        self.btn_copy_ai_suggestion.clicked.connect(lambda: self._copy_to_clipboard(self.txt_ai_suggestion.toPlainText()))
        self.btn_copy_output.clicked.connect(lambda: self._copy_to_clipboard(self.txt_modified_code.toPlainText()))

        self.btn_process_code.clicked.connect(self._on_process_code_clicked)
        self.btn_ai_did_good.clicked.connect(self._on_ai_did_good_clicked)
        self.btn_ai_did_bad.clicked.connect(self._on_ai_did_bad_clicked)

    @Slot()
    def _on_ai_did_good_clicked(self):
        self._log_user_feedback("good")

    @Slot()
    def _on_ai_did_bad_clicked(self):
        self._log_user_feedback("bad")

    def _log_user_feedback(self, assessment: str):
        if not self.session_log_filepath:
            print("ERROR: Session log file not initialized. Cannot log user feedback.")
            # Optionally: inform user via a status bar or dialog
            return
        if not self.last_processed_event_id:
            print("INFO: No code has been processed yet in this session to provide feedback on.")
            # Optionally: inform user
            # self.statusBar().showMessage("Process code first to provide feedback.", 3000)
            return

        feedback_log_entry = {
            "timestamp_unix": time.time(),
            "session_id": self.current_session_id,
            "event_type": "user_feedback",
            "feedback_for_event_id": self.last_processed_event_id,
            "user_assessment": assessment
        }
        try:
            with open(self.session_log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_log_entry) + '\n')
            print(f"INFO: User feedback ('{assessment}') logged for event ID: {self.last_processed_event_id}")
            # Optionally, disable buttons again after feedback for THIS event, or change their state
            # self.btn_ai_did_good.setEnabled(False)
            # self.btn_ai_did_bad.setEnabled(False)
            # Or maybe:
            # self.statusBar().showMessage(f"Feedback '{assessment}' recorded.", 3000)
        except Exception as e:
            print(f"ERROR: Could not write user feedback to log file {self.session_log_filepath}: {e}")
            # self.statusBar().showMessage("Error logging feedback.", 3000)

    @Slot()
    def _on_process_code_clicked(self):
        original_code_text = self.txt_original_code.toPlainText()
        ai_suggestion_text = self.txt_ai_suggestion.toPlainText()

        original_code_for_processing = original_code_text
        if not original_code_text.strip() and self.txt_original_code.placeholderText():
            original_code_for_processing = self.txt_original_code.placeholderText()

        ai_suggestion_for_processing = ai_suggestion_text
        if not ai_suggestion_text.strip() and self.txt_ai_suggestion.placeholderText():
            ai_suggestion_for_processing = self.txt_ai_suggestion.placeholderText()

        # Console prints (user can re-add more detailed ones if desired)
        print("--- Processing Code ---")
        # print(f"Original Code (first 70 chars for processing): {original_code_for_processing[:70].replace(chr(10), ' ')}")
        # print(f"AI Suggestion (first 70 chars for processing): {ai_suggestion_for_processing[:70].replace(chr(10), ' ')}")

        current_event_id = str(uuid.uuid4()) # Define current event_id for this processing run
        self.last_processed_event_id = current_event_id # Update the last processed event ID

        # Enable feedback buttons now that a process is attempted
        self.btn_ai_did_good.setEnabled(True)
        self.btn_ai_did_bad.setEnabled(True)

        # Bookkeeping variables for logging
        raw_instructions_for_log = None
        parsed_instructions_list_for_log = []
        modified_code_for_log = "" # Default to empty string
        system_status_for_log = "SYSTEM_PENDING"
        detailed_error_for_log = None

        try:
            print("Step 1: Asking ReasoningAgent for instructions...")
            # self.statusBar().showMessage("Asking AI for instructions...", 0) # Example status bar
            raw_instructions = self.reasoning_agent.get_instructions(
                original_code_for_processing,
                ai_suggestion_for_processing
            )
            raw_instructions_for_log = raw_instructions
            # print(f"Raw instructions from AI:\n<<<\n{raw_instructions}\n>>>") # Re-add if needed

            if raw_instructions is None: # Handle case where agent returns None
                error_msg = "Error: Reasoning Agent returned no instructions (None)."
                self.txt_modified_code.setPlainText(error_msg)
                system_status_for_log = "SYSTEM_ERROR: ReasoningAgent returned None"
                modified_code_for_log = error_msg
                detailed_error_for_log = "ReasoningAgent.get_instructions returned None"

            elif raw_instructions.strip().upper().startswith("ERROR:"):
                error_msg = f"Error from Reasoning Agent:\n{raw_instructions}"
                self.txt_modified_code.setPlainText(error_msg)
                system_status_for_log = f"SYSTEM_ERROR: ReasoningAgent: {raw_instructions.strip()}"
                modified_code_for_log = error_msg
                detailed_error_for_log = raw_instructions.strip()

            elif raw_instructions.strip().upper() == "NO CHANGES":
                self.txt_modified_code.setPlainText(original_code_for_processing)
                system_status_for_log = "SYSTEM_SUCCESS: NO_CHANGES"
                modified_code_for_log = original_code_for_processing
                print("Processing complete: No changes suggested by AI.")
                # self.statusBar().showMessage("Processing complete: No changes.", 3000)

            else:
                print("Step 2: Parsing instructions...")
                # self.statusBar().showMessage("Parsing instructions...", 0)
                parsed_instructions: list[ParsedInstruction] = parse_instructions(raw_instructions)
                
                # Recommendation: Guard the dataclass serialisation
                if parsed_instructions: # Check if list is not empty
                    parsed_instructions_list_for_log = [
                        dataclasses.asdict(instr) if dataclasses.is_dataclass(instr) else vars(instr)
                        for instr in parsed_instructions
                    ]
                
                if not parsed_instructions: # Handles empty list from parser
                    self.txt_modified_code.setPlainText(original_code_for_processing) # Or some error message
                    system_status_for_log = "SYSTEM_ERROR: Parsing failed or no valid instructions extracted"
                    modified_code_for_log = original_code_for_processing # Or specific error message
                    detailed_error_for_log = "parse_instructions returned an empty list or failed."
                    print("Warning: Parsing resulted in no instructions. Outputting original code.")
                    # self.statusBar().showMessage("Warning: No valid instructions parsed.", 3000)
                else:
                    print(f"Parsed {len(parsed_instructions)} instruction(s).")
                    print("Step 3: Applying instructions to the original code...")
                    # self.statusBar().showMessage("Applying instructions...", 0)
                    modified_code = apply_instructions(original_code_for_processing, parsed_instructions)
                    modified_code_for_log = modified_code
                    self.txt_modified_code.setPlainText(modified_code)
                    system_status_for_log = "SYSTEM_SUCCESS"
                    print("Processing complete. Output area updated.")
                    # self.statusBar().showMessage("Processing complete!", 3000)

        except Exception as e:
            # import traceback # Moved to top-level imports
            error_message = f"An unexpected error occurred during processing:\n{type(e).__name__}: {e}"
            print(error_message)
            traceback.print_exc() # Print full traceback to console for debugging
            self.txt_modified_code.setPlainText(error_message)
            system_status_for_log = f"SYSTEM_ERROR: Unexpected Exception"
            modified_code_for_log = error_message # Log the error message shown to user
            detailed_error_for_log = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            # self.statusBar().showMessage(f"Error: {type(e).__name__}", 3000)
        finally:
            # This block is now guaranteed to run, centralizing the log call
            self._write_processing_log_entry(
                current_event_id, # Use the ID generated for this specific event
                original_code_for_processing,
                ai_suggestion_for_processing,
                raw_instructions_for_log,
                parsed_instructions_list_for_log,
                modified_code_for_log,
                system_status_for_log,
                detailed_error_for_log # Pass the detailed error
            )

    def _write_processing_log_entry(self, event_id, orig_code, ai_sugg, raw_instr, parsed_instr_data, mod_code, status_msg, detailed_error=None):
        if not self.session_log_filepath:
            print("ERROR: Session log file not initialized. Cannot log processing event.")
            return

        # Recommendation: Harden settings access for model name in log
        model_name_for_log = getattr(self.settings, "openai_model", "N/A")

        log_entry = {
            "timestamp_unix": time.time(),
            "session_id": self.current_session_id,
            "event_id": event_id, # Use the passed event_id
            "event_type": "code_processing_event",
            "model_info": {"reasoning_model_name": str(model_name_for_log)}, # Ensure string
            "inputs": {"original_code": orig_code, "ai_suggestion": ai_sugg},
            "processing_stages": {
                "reasoning_agent_llm_output": raw_instr,
                "parsed_instructions": parsed_instr_data, # This is now a list of dicts
            },
            "outputs": {"modified_code": mod_code, "system_status": status_msg}
        }
        if detailed_error: # Add detailed error information if present
            log_entry["detailed_error_info"] = detailed_error

        try:
            with open(self.session_log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            print(f"INFO: Processing event (ID: {event_id}) logged with status: {status_msg}")
        except Exception as e:
            print(f"ERROR: Could not write processing event (ID: {event_id}) to log file {self.session_log_filepath}: {e}")

    @Slot()
    def _open_editor_dialog(self, text_edit_widget, title):
        current_text = text_edit_widget.toPlainText()
        # Use placeholder if text_edit is empty and has a placeholder, otherwise use current_text (even if empty)
        current_text_for_dialog = current_text
        if not current_text.strip() and text_edit_widget.placeholderText() == current_text: # Check if it's actually showing placeholder
             current_text_for_dialog = "" # Open dialog empty if only placeholder is shown

        dialog = CodeEditorDialog(self, window_title=title, initial_text=current_text_for_dialog)
        if dialog.exec(): # This is a blocking call
            text_edit_widget.setPlainText(dialog.get_text())

    @Slot()
    def _copy_to_clipboard(self, text_to_copy):
        if text_to_copy: # Check if there's actually text to copy
            QApplication.clipboard().setText(text_to_copy)
            print("Text copied to clipboard.")
            # self.statusBar().showMessage("Text copied to clipboard.", 2000)
        else:
            print("Nothing to copy.")
            # self.statusBar().showMessage("Nothing to copy.", 2000)

# Placeholder for main execution logic (if this file were to be run directly for testing UI)
if __name__ == '__main__':
    # This is a basic setup for testing the UI in isolation.
    # In the actual app, `main.py` will handle settings creation.
    
    # Mock settings for standalone UI testing
    class MockSettings:
        def __init__(self):
            self.openai_model = "mock_gpt-test"
            self.timeout_seconds = 30
            self.data_dir = "temp_test_data" # Use a temp dir for testing
            # Ensure data_dir exists for the test
            Path(self.data_dir).mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    # If you add a status bar to MainWindow, it would be initialized here
    # e.g., window.statusBar().showMessage("Ready")
    
    mock_settings = MockSettings()
    window = MainWindow(settings=mock_settings)
    window.show()
    sys.exit(app.exec())