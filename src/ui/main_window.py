import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QDialog, QDialogButtonBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QClipboard

# Let's define placeholder texts that your app will use
PLACEHOLDER_ORIGINAL_CODE = "Paste your original code here...\n\n# Example:\ndef hello_world():\n    print(\"Hello, Original World!\")"
PLACEHOLDER_AI_SUGGESTION = "Paste AI's suggested code or instructions here...\n\n# Example:\n# Replace the print statement in hello_world with:\n# print(\"Hello, AI Enhanced World!\")"
PLACEHOLDER_MODIFIED_CODE = "Modified code will appear here..."

class CodeEditorDialog(QDialog):
    def __init__(self, parent=None, window_title="Edit Code", initial_text=""):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setMinimumSize(600, 400) # Start with a decent size

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Good for code
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_text(self):
        return self.text_edit.toPlainText()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code_Slinge V1.0 (MVP)")
        self.setGeometry(100, 100, 1000, 700) # X, Y, Width, Height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_widgets()
        self._setup_layouts()
        self._connect_signals()

    def _create_widgets(self):
        # --- Top Buttons for Expanding Views ---
        self.btn_expand_original = QPushButton("Expand Original Code View")
        self.btn_expand_ai_suggestion = QPushButton("Expand AI Suggestion View")

        # --- Input Text Areas ---
        self.txt_original_code = QTextEdit()
        self.txt_original_code.setPlaceholderText(PLACEHOLDER_ORIGINAL_CODE)
        self.btn_clear_original = QPushButton("Clear")
        self.btn_copy_original = QPushButton("Copy")

        self.txt_ai_suggestion = QTextEdit()
        self.txt_ai_suggestion.setPlaceholderText(PLACEHOLDER_AI_SUGGESTION)
        self.btn_clear_ai_suggestion = QPushButton("Clear")
        self.btn_copy_ai_suggestion = QPushButton("Copy")

        # --- Process Button ---
        self.btn_process_code = QPushButton(">>> PROCESS CODE <<<")
        font = self.btn_process_code.font()
        font.setPointSize(14)
        font.setBold(True)
        self.btn_process_code.setFont(font)
        self.btn_process_code.setFixedHeight(50)


        # --- Output Text Area ---
        self.btn_expand_output = QPushButton("Expand Output Code View")
        self.txt_modified_code = QTextEdit()
        self.txt_modified_code.setPlaceholderText(PLACEHOLDER_MODIFIED_CODE)
        self.txt_modified_code.setReadOnly(False) # User wants this editable in expanded view, so keep it editable here too
        self.btn_clear_output = QPushButton("Clear")
        self.btn_copy_output = QPushButton("Copy")

        # --- Bottom Placeholder Buttons ---
        self.btn_ai_did_good = QPushButton("AI Did Good (Placeholder)")
        self.btn_ai_did_bad = QPushButton("AI Did Bad (Placeholder)")
        self.btn_ai_did_good.setEnabled(False) # Disabled for now
        self.btn_ai_did_bad.setEnabled(False)  # Disabled for now

    def _setup_layouts(self):
        # Top buttons layout
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addWidget(self.btn_expand_original)
        top_buttons_layout.addWidget(self.btn_expand_ai_suggestion)
        self.main_layout.addLayout(top_buttons_layout)

        # Input areas layout
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

        # Process button
        self.main_layout.addWidget(self.btn_process_code, alignment=Qt.AlignmentFlag.AlignCenter)

        # Output area layout
        self.main_layout.addWidget(self.btn_expand_output)
        output_layout = QVBoxLayout() # Using a QVBoxLayout to group output and its buttons
        output_layout.addWidget(self.txt_modified_code)
        output_buttons_layout = QHBoxLayout()
        output_buttons_layout.addWidget(self.btn_clear_output)
        output_buttons_layout.addWidget(self.btn_copy_output)
        output_buttons_layout.addStretch()
        output_layout.addLayout(output_buttons_layout)
        self.main_layout.addLayout(output_layout)


        # Set size policies to make text edits expand
        self.txt_original_code.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.txt_ai_suggestion.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.txt_modified_code.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        # Bottom placeholder buttons layout
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch() # Push buttons to the sides if needed, or center them
        bottom_buttons_layout.addWidget(self.btn_ai_did_good)
        bottom_buttons_layout.addWidget(self.btn_ai_did_bad)
        bottom_buttons_layout.addStretch()
        self.main_layout.addLayout(bottom_buttons_layout)

    def _connect_signals(self):
        # Expand buttons
        self.btn_expand_original.clicked.connect(lambda: self._open_editor_dialog(self.txt_original_code, "Original Code"))
        self.btn_expand_ai_suggestion.clicked.connect(lambda: self._open_editor_dialog(self.txt_ai_suggestion, "AI Suggestion"))
        self.btn_expand_output.clicked.connect(lambda: self._open_editor_dialog(self.txt_modified_code, "Modified Code Output"))

        # Clear buttons
        self.btn_clear_original.clicked.connect(lambda: self.txt_original_code.clear())
        self.btn_clear_ai_suggestion.clicked.connect(lambda: self.txt_ai_suggestion.clear())
        self.btn_clear_output.clicked.connect(lambda: self.txt_modified_code.clear())

        # Copy buttons
        self.btn_copy_original.clicked.connect(lambda: self._copy_to_clipboard(self.txt_original_code.toPlainText()))
        self.btn_copy_ai_suggestion.clicked.connect(lambda: self._copy_to_clipboard(self.txt_ai_suggestion.toPlainText()))
        self.btn_copy_output.clicked.connect(lambda: self._copy_to_clipboard(self.txt_modified_code.toPlainText()))

        # Process button
        self.btn_process_code.clicked.connect(self._on_process_code_clicked)

    @Slot()
    def _open_editor_dialog(self, text_edit_widget, title):
        current_text = text_edit_widget.toPlainText()
        if not current_text.strip() and text_edit_widget.placeholderText(): # If empty and has placeholder
             # For the dialog, let's start with blank rather than placeholder
             # or decide if you want to pass the placeholder to the dialog
            current_text_for_dialog = ""
        else:
            current_text_for_dialog = current_text

        dialog = CodeEditorDialog(self, window_title=title, initial_text=current_text_for_dialog)
        if dialog.exec():
            text_edit_widget.setPlainText(dialog.get_text())

    @Slot()
    def _copy_to_clipboard(self, text_to_copy):
        if text_to_copy:
            clipboard = QApplication.clipboard()
            clipboard.setText(text_to_copy)
            print("Text copied to clipboard.") # TODO: Maybe a status bar message later
        else:
            print("Nothing to copy.")

    @Slot()
    def _on_process_code_clicked(self):
        original_code = self.txt_original_code.toPlainText()
        ai_suggestion = self.txt_ai_suggestion.toPlainText()

         # Your special handling for empty fields (sending placeholder text)
        original_code_for_processing = original_code
        ai_suggestion_for_processing = ai_suggestion

        if not original_code.strip() and self.txt_original_code.placeholderText():
            original_code_for_processing = self.txt_original_code.placeholderText()
            # Preview for print statement, ensuring no problematic backslashes in f-string expression
            preview_orig = original_code_for_processing[:30].replace('\n', ' ').replace('\r', '')
            print(f"Original code field was empty, using placeholder: '{preview_orig}...'")

        if not ai_suggestion.strip() and self.txt_ai_suggestion.placeholderText():
            ai_suggestion_for_processing = self.txt_ai_suggestion.placeholderText()
            # Preview for print statement
            preview_ai = ai_suggestion_for_processing[:30].replace('\n', ' ').replace('\r', '')
            print(f"AI suggestion field was empty, using placeholder: '{preview_ai}...'")

        print("--- Processing Code ---")
        # For printing, it's generally safer to ensure complex data doesn't break f-string syntax
        # However, simple variable access like original_code_for_processing[:50] is usually fine.
        # If these still caused issues (unlikely for this specific error), you'd pre-format them too.
        print(f"Original Code (first 50 chars): {original_code_for_processing[:50]}")
        print(f"AI Suggestion (first 50 chars): {ai_suggestion_for_processing[:50]}")
        print("-------------------------")

        # --- THIS IS WHERE YOU'LL INTEGRATE YOUR CORE LOGIC ---
        # (Comments for your actual logic integration remain here)
        # ...
        # -------------------------------------------------------
        
        # For now, just a placeholder action:
        # Pre-process the strings for the f-string to avoid the backslash issue
        original_preview_for_output = original_code_for_processing[:30].replace('\n', ' ').replace('\r', '')
        suggestion_preview_for_output = ai_suggestion_for_processing[:30].replace('\n', ' ').replace('\r', '')

        processed_text = (
            f"--- SIMULATED PROCESSED OUTPUT ---\n"
            f"Based on Original (starts with: '{original_preview_for_output}...')\n"
            f"And AI Suggestion (starts with: '{suggestion_preview_for_output}...')\n"
            f"\nYour amazing Code_Slinge logic would go here!"
        )
        self.txt_modified_code.setPlainText(processed_text)
        print("Processing complete (simulated). Output area updated.")

