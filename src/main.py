from PyQt5.QtWidgets import QApplication
import sys
from src.windows.window_manager import open_login_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    open_login_window()
    sys.exit(app.exec_())
