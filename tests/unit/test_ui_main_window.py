# tests/unit/test_ui_main_window.py
import pytest
from PySide6.QtCore import Qt
from unittest.mock import patch

# VVVV THIS LINE RIGHT HERE VVVV
from src.ui.main_window import MainWindow, CodeEditorDialog, PLACEHOLDER_ORIGINAL_CODE, PLACEHOLDER_AI_SUGGESTION
# ^^^^ MAKE SURE PLACEHOLDER_AI_SUGGESTION IS INCLUDED ^^^^

# Qt Bot is the main fixture from pytest-qt to interact with Qt widgets
def test_mainwindow_instantiation(qtbot):
    """Test if the MainWindow can be created."""
    main_window = MainWindow()
    qtbot.addWidget(main_window) # Add the widget to qtbot for proper cleanup
    assert main_window is not None
    assert main_window.windowTitle() == "Code_Slinge V1.0 (MVP)"
    # You can add more assertions here, e.g., checking if certain widgets exist
    assert main_window.txt_original_code is not None
    assert main_window.txt_ai_suggestion is not None
    assert main_window.txt_modified_code is not None
    assert main_window.btn_process_code is not None

def test_codeeditordialog_instantiation_and_text(qtbot):
    """Test if CodeEditorDialog can be created and handles text."""
    initial_text = "Hello, Test World!"
    dialog = CodeEditorDialog(window_title="Test Dialog", initial_text=initial_text)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Test Dialog"
    assert dialog.get_text() == initial_text

    # Simulate setting new text and getting it (as if user typed and hit OK)
    new_text = "New test text"
    dialog.text_edit.setPlainText(new_text)
    assert dialog.get_text() == new_text # Before accept/reject

def test_mainwindow_clear_original_code_button(qtbot):
    """Test the 'Clear' button for the original code text edit."""
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Set some initial text
    initial_content = "Some original code here"
    main_window.txt_original_code.setPlainText(initial_content)
    assert main_window.txt_original_code.toPlainText() == initial_content

    # Spy on the clear method of the QTextEdit to ensure it's called
    # For more complex scenarios, you might mock a method in your MainWindow class
    # but for direct widget manipulation, checking the widget state is often enough.
    
    # Simulate the button click
    # The clear button calls lambda: self.txt_original_code.clear()
    # So we can directly test the effect of that lambda
    qtbot.mouseClick(main_window.btn_clear_original, Qt.MouseButton.LeftButton)

    # Check if the text edit is cleared
    # It should clear to an empty string, not the placeholder text,
    # as clear() method does that.
    assert main_window.txt_original_code.toPlainText() == ""
    
    # If you wanted to ensure the placeholder is visible, you'd need a more complex check
    # or if the clear button also explicitly set the placeholder, but QTextEdit.clear()
    # just empties the content. The placeholder appears visually due to Qt's handling.

def test_mainwindow_process_code_button_placeholder_logic(qtbot, mocker):
    """Test that the process code button uses placeholder text if fields are empty."""
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Mock the _on_process_code_clicked method to check what it would do,
    # or simply check the state of inputs when it's called.
    # For this test, let's spy on the print statements to see if placeholders are used.
    mock_print = mocker.patch('builtins.print')

    # Ensure text areas are empty (so placeholder text logic should trigger)
    main_window.txt_original_code.clear()
    main_window.txt_ai_suggestion.clear()
    
    # Simulate clicking the process button
    qtbot.mouseClick(main_window.btn_process_code, Qt.MouseButton.LeftButton)

    # Check if print was called with messages indicating placeholder usage
    # This is a bit fragile as it depends on exact print statements,
    # a better way would be to check the variables passed to the backend.
    # For now, this demonstrates the idea.
    
    # Expected messages when placeholders are used by the print statements in _on_process_code_clicked
    # We need to check args of the call.
    # `original_code = self.txt_original_code.placeholderText()`
    # `ai_suggestion = self.txt_ai_suggestion.placeholderText()`
    # Then it prints: `print(f"Original code field was empty, using placeholder: '{original_code[:30]}...'")`

    # Let's check if the output text area received the simulated output
    # that includes the placeholders
    output_text = main_window.txt_modified_code.toPlainText()
    assert PLACEHOLDER_ORIGINAL_CODE[:30] in output_text
    assert PLACEHOLDER_AI_SUGGESTION[:30] in output_text
    
    # More robust: check that the actual backend call (when we integrate it)
    # would receive these placeholder strings. For now, the print check can be:
    found_original_placeholder_log = False
    found_ai_placeholder_log = False
    for call_args in mock_print.call_args_list:
        arg_tuple = call_args[0] # print is called with a single string argument
        if arg_tuple: # Ensure it's not an empty call
            log_message = str(arg_tuple[0])
            if f"Original code field was empty, using placeholder: '{PLACEHOLDER_ORIGINAL_CODE[:30]}" in log_message:
                found_original_placeholder_log = True
            if f"AI suggestion field was empty, using placeholder: '{PLACEHOLDER_AI_SUGGESTION[:30]}" in log_message:
                found_ai_placeholder_log = True
    
    assert found_original_placeholder_log, "Log for original code placeholder not found"
    assert found_ai_placeholder_log, "Log for AI suggestion placeholder not found"


# To run these tests:
# 1. Make sure you have pytest and pytest-qt installed.
# 2. Navigate to your project root in the terminal.
# 3. Run the command: pytest