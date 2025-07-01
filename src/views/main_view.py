from PyQt5 import uic  # Thêm uic để load file .ui trực tiếp
from PyQt5.QtWidgets import QMainWindow

from src.controllers.buttonController import buttonController
from src.controllers.student.studentListController import StudentListController
from src.utils.changeTab import MenuNavigator
from src.views.moveable_window import MoveableWindow
from src.controllers.logoutController import LogoutController
from src.utils.ui_utils import set_user_info


class MainWindow(QMainWindow, MoveableWindow):
    def __init__(self, username):
        super().__init__()
        # Load file .ui trực tiếp
        uic.loadUi("../UI/forms/mainWindowApp.ui", self)
        MoveableWindow.__init__(self)
        # Ví dụ đổi nội dung userInfoLabel
        set_user_info(self.userInfoLabel, username)
        # ẩn khung mặc định
        self.invisible()
        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)
        # Tạo controller, truyền self vào
        self.logout_controller = LogoutController(self)
        # Gắn nút logout
        self.logoutBtn.clicked.connect(lambda: self.logout_controller.handle_logout())
        # Gắn sự kiện nút ( nút close, nút hidden)
        self.closeBtn.clicked.connect(self.buttonController.handle_close)
        self.hiddenBtn.clicked.connect(self.buttonController.handle_hidden)
        # Gắn nút ( nút maximize, nút restore)
        self.maximizeBtn.clicked.connect(self.buttonController.toggle_maximize_restore)
        self.restoreBtn.clicked.connect(self.buttonController.toggle_maximize_restore)
        # Ẩn nút restore lúc đầu
        self.restoreBtn.hide()

        # Tạo controller, truyền self vào
        buttons = [
            self.dashboard,
            self.studentList,
            self.scores,
            self.classroom,
            self.tulitionFee,
            self.lecturer,
            self.notification
        ]
        index_map = {btn: i for i, btn in enumerate(buttons)}

        self.menu_nav = MenuNavigator(self.stackedWidget, buttons, index_map, default_button=self.dashboard)

        # # Gán nút ( add char )
        self.studentListController = StudentListController(
            self.tableList,
            parent=self,
            edit_button=self.editStudentBtn  # ✅
        )

        self.addStudentBtn.clicked.connect(self.studentListController.open_add_student_dialog)
        self.editStudentBtn.clicked.connect(self.studentListController.handle_edit_button_clicked)

        print("DEBUG >> tableList:", self.tableList)
        self.studentListController.load_students_to_table()













