from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QPropertyAnimation
from src.models.user_model import check_login

class LoginController:
    def __init__(self, view):
        self.view = view

    def handle_login(self, username, password):
        print(f"DEBUG: Trying login with {username}/{password}")
        if check_login(username, password):
            print("DEBUG: Login success")
            self.on_login_success()
        else:
            print("DEBUG: Login failed")
            self.on_login_failed()

    def on_login_success(self):
        QMessageBox.information(self.view, "Login", "✅ Đăng nhập thành công!")
        # TODO: Chuyển sang màn hình chính
        # main_window = MainAppWindow()
        # main_window.show()
        # self.view.close()

    def on_login_failed(self):
        QMessageBox.warning(self.view, "Login", "❌ Tài khoản hoặc mật khẩu sai!")

    def handle_close(self):
        self.view.close()

    def handle_hidden(self):
        self.fade_animation = QPropertyAnimation(self.view, b"windowOpacity")
        self.fade_animation.setDuration(100)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self._minimize)
        self.fade_animation.start()

    def _minimize(self):
        self.view.showMinimized()
        self.view.setWindowOpacity(1.0)

