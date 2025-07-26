from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from src.controllers.buttonController import buttonController
from src.controllers.dashboard.dashboardController import dashboardController
from src.controllers.student.studentListController import StudentListController
from src.controllers.student.studentScoreController import StudentScoreController
from src.models.user_model import get_user_by_username, get_teacher_context
from src.utils.changeTab import MenuNavigator
from src.views.moveable_window import MoveableWindow
from src.controllers.logoutController import LogoutController
from src.utils.ui_utils import set_user_info


class MainWindow(QMainWindow, MoveableWindow):
    def __init__(self, username):
        super().__init__()
        uic.loadUi("../UI/forms/mainWindowApp.ui", self)
        MoveableWindow.__init__(self)

        # THÊM CÁC DÒNG NÀY ĐỂ QUẢN LÝ NGƯỜI DÙNG
        self.current_username = username
        self.teacher_context = None
        self._load_user_context()  # Tải context ngay khi khởi tạo
        # -------------------

        set_user_info(self.userInfoLabel, username)
        self.invisible()
        self.buttonController = buttonController(self)
        self.logout_controller = LogoutController(self)
        self.logoutBtn.clicked.connect(lambda: self.logout_controller.handle_logout())
        self.closeBtn.clicked.connect(self.buttonController.handle_close)
        self.hiddenBtn.clicked.connect(self.buttonController.handle_hidden)
        self.maximizeBtn.clicked.connect(self.buttonController.toggle_maximize_restore)
        self.restoreBtn.clicked.connect(self.buttonController.toggle_maximize_restore)
        self.restoreBtn.hide()

        buttons = [
            self.dashboard, self.student, self.scores,
            self.classroom, self.subject, self.notification
        ]
        index_map = {btn: i for i, btn in enumerate(buttons)}
        self.menu_nav = MenuNavigator(self.stackedWidget, buttons, index_map, default_button=self.dashboard)

        self.dashboardController = dashboardController(parent=self)

        self.studentListController = StudentListController(
            self.studentList,
            parent=self,
            student_page=self.Student_page
        )

        self.studentScoreController = StudentScoreController(
            self.scoresList,
            parent=self,
            edit_button=self.editScoreBtn,
            score_page=self.Scores_page
        )
        self.addScoreBtn.clicked.connect(self.studentScoreController.handle_add_button_clicked)
        self.editScoreBtn.clicked.connect(self.studentScoreController.handle_edit_button_clicked)

        self.stackedWidget.currentChanged.connect(self.on_tab_changed)

        # Chủ động tải Dashboard lần đầu tiên nếu nó là tab mặc định
        if self.stackedWidget.currentWidget() == self.Dashboard_page:
            self.on_tab_changed(self.stackedWidget.currentIndex())

        self.on_tab_changed(self.stackedWidget.currentIndex())

    # THÊM HÀM MỚI NÀY
    def _load_user_context(self):
        """Lấy thông tin và quyền hạn của người dùng từ database."""
        user_info = get_user_by_username(self.current_username)

        if not user_info:
            print(f"❌ Không tìm thấy người dùng: {self.current_username}")
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy thông tin người dùng.")
            self.close()
            return

        role = user_info.get("role", "").lower()

        if role == "admin":
            print("👤 Admin đăng nhập. Full access mode.")
            self.user_context = {
                "username": self.current_username,
                "role": "admin",
                "teacher_info": None
            }
            self.teacher_context = None  # Giữ để tương thích cũ
        elif role == "teacher":
            self.teacher_context = get_teacher_context(self.current_username)
            if not self.teacher_context:
                QMessageBox.critical(self, "Lỗi phân quyền", f"Tài khoản '{self.current_username}' chưa được phân công lớp.")
                self.close()
                return

            print(f"✅ Đã tải context cho giáo viên: {self.teacher_context.get('teacher_name')}")
            print("📋 Chi tiết:", self.teacher_context)

            self.user_context = {
                "username": self.current_username,
                "role": "teacher",
                "teacher_info": self.teacher_context
            }
        else:
            print(f"❌ Vai trò không hợp lệ: {role}")
            QMessageBox.critical(self, "Lỗi", "Người dùng không có quyền truy cập.")
            self.close()

    # CHỈNH SỬA HÀM on_tab_changed
    def on_tab_changed(self, index):
        current_widget = self.stackedWidget.widget(index)

        # Mặc định một tiêu đề, hoặc để trống
        new_title = "Student Management System"

        if current_widget == self.Dashboard_page:
            # Đặt lại tiêu đề
            new_title = "Dashboard"

            print("📊 Đã chuyển đến trang Dashboard")
            if not self.dashboardController._initialized_for_user:
                self.dashboardController.setup_for_user(self.teacher_context)

        elif current_widget == self.Student_page:
            # Đặt lại tiêu đề
            new_title = "Student List"  # Hoặc "Danh sách Sinh viên"

            print("📘 Đã chuyển đến trang Student List")
            if not self.studentListController._initialized_for_user:
                self.studentListController.setup_for_user(self.teacher_context)

        elif current_widget == self.Scores_page:
            # Đặt lại tiêu đề
            new_title = "Score Management"  # Hoặc "Quản lý Điểm"

            print("📝 Đã chuyển đến trang Scores")
            if not self.studentScoreController._initialized_for_user:
                self.studentScoreController.setup_for_user(self.teacher_context)

        # elif current_widget == self.Classroom_page:
        #     # Đặt lại tiêu đề
        #     new_title = "Classroom Management"  # Hoặc "Quản lý Lớp"
        #
        #     print("📝 Đã chuyển đến trang Classroom")
        #     if not self.classroomController._initialized_for_user:
        #         self.studentScoreController.setup_for_user(self.teacher_context)
        #
        # elif current_widget == self.Subject_page:
        #     # Đặt lại tiêu đề
        #     new_title = "Subject Management"  # Hoặc "Quản lý Môn học"
        #
        #     print("📝 Đã chuyển đến trang Subject")
        #     if not self.subjectController._initialized_for_user:
        #         self.subjectController.setup_for_user(self.teacher_context)
        #
        # elif current_widget == self.Notification_page:
        #     # Đặt lại tiêu đề
        #     new_title = "Notification Management"  # Hoặc "Quản lý Thống báo"
        #
        #     print("📝 Đã chuyển đến trang Notification")
        #     if not self.notificationController._initialized_for_user:
        #         self.notificationController.setup_for_user(self.teacher_context)

        self.header_DBD.setText(new_title)


