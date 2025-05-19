# tests/unit/test_main_entry.py
import pytest
from unittest.mock import MagicMock

# Import the main script to be tested
import main as main_module_under_test

import main as main_module_under_test

class MockSysExit(BaseException): # Inherit from BaseException like SystemExit does
    """Custom exception to simulate sys.exit behavior more accurately in tests."""
    def __init__(self, code=None):
        print(f"DEBUG: MockSysExit.__init__ called with code={code} (type: {type(code)})") # <--- ADD THIS DEBUG PRINT
        self.code = code
        super().__init__(f"MockSysExit with code {code}")




def test_main_function_happy_path(mocker):
    """
    Tests the main application flow when settings load successfully.
    """
    # Patch names as they are accessed within main_module_under_test
    # Use 'mocker.patch.object' to patch attributes of an already imported module
    mock_get_settings = mocker.patch.object(main_module_under_test, 'get_settings')
    mock_qapplication_constructor = mocker.patch.object(main_module_under_test, 'QApplication')
    mock_mainwindow_constructor = mocker.patch.object(main_module_under_test, 'MainWindow')
    
    # Patch 'exit' directly on the 'sys' module that main_module_under_test imported
    mock_sys_exit = mocker.patch.object(main_module_under_test.sys, 'exit')

    # Define the behavior of our mocks
    mock_settings_instance = MagicMock()
    mock_settings_instance.openai_model = "test_gpt_model"
    mock_get_settings.return_value = mock_settings_instance

    mock_app_instance = MagicMock()
    mock_qapplication_constructor.return_value = mock_app_instance
    mock_app_instance.exec.return_value = 0 

    mock_window_instance = MagicMock()
    mock_mainwindow_constructor.return_value = mock_window_instance

    main_module_under_test.main()

    mock_get_settings.assert_called_once()
    mock_qapplication_constructor.assert_called_once_with(main_module_under_test.sys.argv)
    mock_mainwindow_constructor.assert_called_once_with(settings=mock_settings_instance)
    mock_window_instance.show.assert_called_once()
    mock_app_instance.exec.assert_called_once()
    mock_sys_exit.assert_called_once_with(0)



def _raise_mock_sys_exit_with_arg(*args, **kwargs):
    """
    Helper function for side_effect.
    Takes arguments passed to the mock (sys.exit) and uses the first one
    to instantiate and raise MockSysExit.
    """
    # sys.exit() is typically called with one positional argument (the status code)
    # If called with no args, it implies exit code 0.
    # If called with sys.exit(None), it also implies exit code 0.
    # Our MockSysExit's __init__ defaults 'code' to None if no arg is passed.
    # This logic tries to replicate that: if args is empty, pass nothing to MockSysExit
    # so its internal default (None) is used. If args has something, pass the first element.
    exit_code_to_pass_to_exception = args[0] if args else None
    raise MockSysExit(exit_code_to_pass_to_exception)






def test_main_function_settings_load_failure(mocker):
    """
    Tests the main application flow when get_settings() raises an exception.
    """
    mock_get_settings = mocker.patch.object(main_module_under_test, 'get_settings', 
                                            side_effect=Exception("Settings load failed!"))
    
    # CHANGE THIS LINE: Add side_effect=MockSysExit
    mock_sys_exit = mocker.patch.object(
        main_module_under_test.sys, 
        'exit', 
        side_effect=_raise_mock_sys_exit_with_arg  # <--- Ensures sys.exit will raise our custom exception
    )

    mock_qapp_constructor = mocker.patch.object(main_module_under_test, 'QApplication')
    mock_mainwindow_constructor = mocker.patch.object(main_module_under_test, 'MainWindow')

    # CHANGE THIS BLOCK: Wrap the call in pytest.raises and adjust assertions
    with pytest.raises(MockSysExit) as excinfo:
        main_module_under_test.main()

    # Assertions
    mock_get_settings.assert_called_once()
    
    # Check that sys.exit was called (which raised MockSysExit) and check the exit code
    mock_sys_exit.assert_called_once_with(1) # The mock was called with 1 before raising
    assert excinfo.value.code == 1          # The exception instance should have the code

    # Crucially, ensure that QApplication and MainWindow were not initialized
    # because MockSysExit should have halted execution before these lines.
    mock_qapp_constructor.assert_not_called()
    mock_mainwindow_constructor.assert_not_called()