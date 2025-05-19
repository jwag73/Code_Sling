# main.py (in the root of your project)
import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config.settings import get_settings

def main():
    try:
        settings = get_settings()
        print(f"Settings loaded. OpenAI Model: {settings.openai_model}")
    except Exception as e:
        print(f"Fatal Error: Could not load settings. {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    # Pass the 'settings' object to MainWindow's constructor
    window = MainWindow(settings=settings) 
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()