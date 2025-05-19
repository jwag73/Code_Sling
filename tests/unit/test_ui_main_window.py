# tests/unit/test_ui_main_window.py
import pytest
from PySide6.QtCore import Qt
from unittest.mock import patch, MagicMock # Make sure MagicMock is imported
from pathlib import Path # Import Path

from src.ui.main_window import MainWindow, CodeEditorDialog, PLACEHOLDER_ORIGINAL_CODE, PLACEHOLDER_AI_SUGGESTION
from src.config.settings import AppSettings # Import AppSettings for type hinting/spec

import builtins # Import builtins to access the original print

# Define a fixture for mock AppSettings
@pytest.fixture
def mock_app_settings(tmp_path: Path) -> AppSettings: # tmp_path is a built-in pytest fixture
    """Provides a mock AppSettings object for MainWindow tests."""
    settings = MagicMock(spec=AppSettings)
    settings.openai_api_key = "test_api_key_for_ui"
    settings.openai_model = "test_model_for_ui"
    settings.timeout_seconds = 10
    # Use tmp_path to ensure data_dir is a temporary, writeable path
    settings.data_dir = tmp_path / "app_data"
    # MainWindow._start_new_session will create subdirectories,
    # so settings.data_dir itself doesn't need mkdir here.
    settings.log_level = "DEBUG" # Or any appropriate default
    return settings



# Qt Bot is the main fixture from pytest-qt to interact with Qt widgets
def test_mainwindow_instantiation(qtbot, mock_app_settings: AppSettings): # Add mock_app_settings
    """Test if the MainWindow can be created."""
    main_window = MainWindow(settings=mock_app_settings) # Pass the settings
    qtbot.addWidget(main_window) # Add the widget to qtbot for proper cleanup
    assert main_window is not None
    assert main_window.windowTitle() == "Code_Slinge V1.0 (MVP)"
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

def test_mainwindow_clear_original_code_button(qtbot, mock_app_settings: AppSettings): # <-- Add fixture here
    """Test the 'Clear' button for the original code text edit."""
    main_window = MainWindow(settings=mock_app_settings) # <-- Use fixture here
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

# In tests/unit/test_ui_main_window.py

# In tests/unit/test_ui_main_window.py

def test_mainwindow_process_code_button_placeholder_logic(qtbot, mocker, mock_app_settings: AppSettings):
    # Store the original print function
    real_print = builtins.print # <--- ADD THIS LINE

    main_window = MainWindow(settings=mock_app_settings)
    qtbot.addWidget(main_window)

    mock_print = mocker.patch('builtins.print') # Now 'print' is mocked

    main_window.txt_original_code.clear()
    main_window.txt_ai_suggestion.clear()

    mock_get_instructions = mocker.patch.object(main_window.reasoning_agent, 'get_instructions')
    mock_get_instructions.return_value = "NO CHANGES"
    
    qtbot.mouseClick(main_window.btn_process_code, Qt.MouseButton.LeftButton)

    # ----- START REVISED DEBUGGING PRINT (using real_print) -----
    real_print("\nDEBUG: mock_print.call_args_list inspection:") # Use real_print

    try:
        num_calls = len(mock_print.call_args_list)
        real_print(f"DEBUG: Total calls captured by mock_print: {num_calls}") # Use real_print

        if num_calls == 0:
            real_print("DEBUG: mock_print.call_args_list is EMPTY!") # Use real_print
        else:
            indices_to_inspect = list(range(min(num_calls, 3))) 
            if num_calls > 6: 
                indices_to_inspect.extend(list(range(max(3, num_calls - 3), num_calls)))
            
            processed_indices = []
            for idx in indices_to_inspect:
                if idx not in processed_indices:
                    processed_indices.append(idx)
            indices_to_inspect = sorted(processed_indices)

            real_print(f"DEBUG: Will inspect indices: {indices_to_inspect}") # Use real_print

            for i in indices_to_inspect:
                call_obj = mock_print.call_args_list[i]
                real_print(f"\nDEBUG: Inspecting captured print call index {i}:") # Use real_print
                
                positional_args = call_obj[0]
                keyword_args = call_obj[1]

                if positional_args: 
                    arg_to_inspect = positional_args[0] 
                    real_print(f"  Arg 0 type: {type(arg_to_inspect)}") # Use real_print
                    try:
                        if isinstance(arg_to_inspect, (str, list, tuple, dict, bytes)):
                            real_print(f"  Arg 0 length: {len(arg_to_inspect)}") # Use real_print
                        
                        preview = repr(arg_to_inspect)
                        if len(preview) > 150: 
                            preview = preview[:150] + "... (repr truncated)"
                        real_print(f"  Arg 0 preview (repr): {preview}") # Use real_print

                    except Exception as e_inspect:
                        real_print(f"  Error during inspection of arg 0: {type(e_inspect).__name__} - {e_inspect}") # Use real_print
                else:
                     real_print(f"  Call {i} had no positional args.") # Use real_print
                
                if keyword_args:
                    real_print(f"  Keyword args: {keyword_args}") # Use real_print

    except Exception as e_outer_debug:
        real_print(f"DEBUG: Error during mock_print inspection block: {type(e_outer_debug).__name__} - {e_outer_debug}") # Use real_print
    
    real_print("----- END REVISED DEBUGGING PRINT -----") # Use real_print
    # ----- Assertions ----- (rest of your test follows)


    

    iteration_limit = 1000 
    calls_to_check = mock_print.call_args_list # This is still correct, we want to check the mock's calls
    
    if len(calls_to_check) > iteration_limit:
        real_print(f"WARNING: Too many print calls ({len(calls_to_check)}), checking only the first {iteration_limit} for assertions.") # Use real_print
        calls_to_check = mock_print.call_args_list[:iteration_limit]


    
 

    mock_get_instructions.assert_called_once_with(
        PLACEHOLDER_ORIGINAL_CODE, 
        PLACEHOLDER_AI_SUGGESTION
    )

    output_text = main_window.txt_modified_code.toPlainText()
    assert output_text == PLACEHOLDER_ORIGINAL_CODE, \
        f"Expected output to be original placeholder, but got: {output_text}"
