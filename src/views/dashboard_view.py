from PyQt5 import uic  # Thêm uic để load file .ui trực tiếp
from PyQt5.QtCore import Qt
from src.controllers.buttonController import buttonController
from src.views.moveable_window import MoveableWindow
from src.controllers.logoutController import LogoutController


class DashboardWindow(MoveableWindow):
    def __init__(self, username):
        super().__init__()
        # Load file .ui trực tiếp
        uic.loadUi("../UI/forms/dashboardWindow.ui", self)

        # Ví dụ đổi nội dung userInfoLabel
        self.userInfoLabel.setText(f"👤 {username} (Online 🟢)")

        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)

        # Tạo controller, truyền self vào
        self.logout_controller = LogoutController(self)

        # Gắn nút logout
        self.logoutBtn.clicked.connect(lambda: self.logout_controller.handle_logout())


        # Gắn sự kiện nút
        self.closeBtn.clicked.connect(self.buttonController.handle_close)
        self.hiddenBtn.clicked.connect(self.buttonController.handle_hidden)

        # Gắn nút
        self.maximizeBtn.clicked.connect(self.buttonController.toggle_maximize_restore)
        self.restoreBtn.clicked.connect(self.buttonController.toggle_maximize_restore)

        # Ẩn nút restore lúc đầu
        self.restoreBtn.hide()

        # Thêm frameless + trong suốt
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)




