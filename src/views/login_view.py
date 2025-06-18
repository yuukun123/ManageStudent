from PyQt5 import uic
from PyQt5.QtCore import Qt
from src.controllers.LoginController import LoginController
from src.views.moveable_window import MoveableWindow
from src.controllers.buttonController import buttonController

class LoginWindow(MoveableWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("../UI/forms/login.ui", self)

        # Thêm frameless + trong suốt
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowOpacity(1.0)

        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)

        # Tạo controller, truyền self vào
        self.controller = LoginController(self)

        # Gắn nút
        self.loginBtn.clicked.connect(lambda: self.controller.handle_login(
            self.userName.text(), self.password.text()
        ))
        self.closeBtn.clicked.connect(self.buttonController.handle_close)
        self.hiddenBtn.clicked.connect(self.buttonController.handle_hidden)

