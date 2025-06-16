from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QPropertyAnimation
from UI.forms.login_ui import Ui_MainWindow
from src.controllers.LoginController import LoginController

class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowOpacity(1.0)

        self.controller = LoginController(self)
        # Gắn nút
        self.ui.loginBtn.clicked.connect(lambda: self.controller.handle_login(
            self.ui.userName.text(), self.ui.password.text()
        ))
        self.ui.closeBtn.clicked.connect(self.controller.handle_close)
        self.ui.hiddenBtn.clicked.connect(self.controller.handle_hidden)

    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(100)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()
