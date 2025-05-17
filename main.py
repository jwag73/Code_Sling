# main.py (in the root of your project)
import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config.settings import get_settings # <<<< IMPORT get_settings

def main():
    # Initialize application settings using your helper function
    try:
        settings = get_settings() # <<<< USE get_settings()
        # You can now use the 'settings' object if needed here,
        # or pass it to MainWindow if MainWindow's __init__ accepts it.
        # Components that need settings can also import get_settings() themselves.
        print(f"Settings loaded. OpenAI Model: {settings.openai_model}") # Example usage
    except Exception as e:
        print(f"Fatal Error: Could not load settings. {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow() # Pass 'settings' here if needed: MainWindow(settings=settings)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()