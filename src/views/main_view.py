from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget

from src.controllers.buttonController import buttonController
from src.controllers.dashboard.dashboardController import dashboardController
from src.controllers.student.studentListController import StudentListController
from src.controllers.student.studentScoreController import StudentScoreController
from src.controllers.classroom.classroomController import ClassroomController

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

        self.setResizeOnDrag(True, mini_size=QSize(1434, 854))

        # Kết nối tín hiệu từ MoveableWindow để cập nhật UI của nút
        self.size_state_changed.connect(self._update_mini_restore_button_ui)

        # 4. CẬP NHẬT GIAO DIỆN NÚT BẤM LẦN ĐẦU
        self._update_mini_restore_button_ui()

        # THÊM CÁC DÒNG NÀY ĐỂ QUẢN LÝ NGƯỜI DÙNG
        self.current_username = username
        self.teacher_context = None
        self._load_user_context()  # Tải context ngay khi khởi tạo
        # -------------------

        # self.header_4 = QWidget()
        # self.header_4.setObjectName("header_4")
        # self.verticalLayout_2.addWidget(self.header_4)
        self.header_4.hide()

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

        self.classroomController = ClassroomController(
            self.area2,
            parent=self,
            # classroom_page = self.Classroom_page
        )

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

        self.disable_unfinished_features()
        self.on_tab_changed(self.stackedWidget.currentIndex())

    def mouseDoubleClickEvent(self, event):
        """
        Bắt sự kiện double-click để toggle mini-size và maximize.
        """
        if event.button() == Qt.LeftButton:
            # Double-click vào thanh tiêu đề (ví dụ: vùng y < 50)
            if event.y() < 50:
                # Ưu tiên hành động maximize/restore trước
                self.buttonController.toggle_maximize_restore()

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

        elif current_widget == self.Classroom_page:
            # Đặt lại tiêu đề
            new_title = "Classroom Management"  # Hoặc "Quản lý Lớp"

            print("📝 Đã chuyển đến trang Classroom")
            if not self.classroomController._initialized_for_user:
                self.classroomController.setup_for_user(self.teacher_context)

        self.header_DBD.setText(new_title)

    def disable_unfinished_features(self):
        """Vô hiệu hóa các nút menu cho các tính năng chưa hoàn thiện."""

        # 1. Vô hiệu hóa nút
        self.notification.setEnabled(False)  # Giả sử objectName của nút là 'notification'
        self.subject.setEnabled(False)  # Giả sử objectName của nút là 'subject'

        # 2. (Tùy chọn) Thêm Tooltip để giải thích cho người dùng
        self.notification.setToolTip("Tính năng đang được phát triển")
        self.subject.setToolTip("Tính năng đang được phát triển")

        # 3. (Tùy chọn) Thay đổi style để trông "bị vô hiệu hóa" rõ hơn
        disabled_style = "background-color: #d3d3d3; color: #888888; border-radius: 6px;"
        self.notification.setStyleSheet(disabled_style)
        self.subject.setStyleSheet(disabled_style)

    def toggle_mini_restore(self):
        """
        Chuyển đổi giữa kích thước mini và kích thước ban đầu.
        Được gọi bởi nút bấm hoặc double-click.
        """
        # Bỏ qua nếu đang ở trạng thái phóng to tối đa
        if self.isMaximized():
            return

        if not self.resize_on_drag_enabled:
            return

        if self.is_mini_size:
            # Nếu đang là mini, quay về hình dạng ban đầu
            if self._original_geometry:
                self.setGeometry(self._original_geometry)
            self.is_mini_size = False
        else:
            # Nếu đang là kích thước thường, lưu hình dạng và chuyển sang mini
            self._original_geometry = self.geometry()
            current_center = self._original_geometry.center()

            self.resize(self.mini_size)

            new_geo = self.frameGeometry()
            new_geo.moveCenter(current_center)
            self.move(new_geo.topLeft())

            self.is_mini_size = True

        # Sau khi thay đổi trạng thái, cập nhật lại UI của nút
        self._update_mini_restore_button_ui()

    def _update_mini_restore_button_ui(self):
        """Cập nhật icon và tooltip cho nút toggle."""
        if self.is_mini_size:
            # Giả sử bạn có 2 nút riêng biệt giống như maximize/restore
            # self.maximizeBtn.hide()
            # self.restoreBtn.show()

            self.restoreBtn.setIcon(QIcon("../UI/icons/copy.svg"))
        else:
            # Đang bình thường -> Nút phải có chức năng "thu nhỏ"
            # self.maximizeBtn.show()
            # self.restoreBtn.hide()

            self.restoreBtn.setIcon(QIcon("../UI/icons/copy.svg"))



