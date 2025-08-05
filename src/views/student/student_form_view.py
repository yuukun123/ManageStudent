from PyQt5 import uic
from PyQt5.QtCore import QDate, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from src.constants.form_mode import FormMode
from src.controllers.buttonController import buttonController
from src.controllers.student.studentFormController import StudentFormController
# from src.utils.changeTab import MenuNavigator
from src.views.moveable_window import MoveableWindow


class StudentForm(QDialog, MoveableWindow):
    def __init__(self, parent=None, mode="add", student_data=None, default_faculty_id=None, default_class_id=None, subject_id=None, class_subject_id=None, year=None):
        super().__init__(parent)
        uic.loadUi("../UI/forms/score_form.ui", self)
        MoveableWindow.__init__(self)
        # self.invisible()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.student_id_to_edit = None
        self.subject_id = subject_id
        self.class_subject_id = class_subject_id
        self.year = year
        # self.student_id_to_save = student_data.get('id') if student_data else None  # Lưu lại ID sinh viên
        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)
        # Gán nút
        self.cancelBtn.clicked.connect(self.buttonController.handle_cancel)
        self.controller = StudentFormController(self, subject_id=self.subject_id)

        # if default_faculty_id is not None and default_class_id is not None:
        #     # Giả sử trong form này bạn có một ComboBox tên là facultyComboBox
        #     index = self.filterFacultyScore.findData(default_faculty_id)
        #     if index != -1:
        #         self.filterFacultyScore.setCurrentIndex(index)

        self.inputMidtermScore.textChanged.connect(self.controller.calculate_process_score)
        self.inputFinalScore.textChanged.connect(self.controller.calculate_process_score)


        # Tùy chỉnh giao diện theo mode
        if mode == FormMode.ADD:
            self.labelForm.setText("Add New Student")
            self.okBtn.setText("Ok")

            if not student_data:
                print("⚠️ student_data is None")
                self.reject()
                return

            # Load data
            self.inputStdID.setText(student_data.get("student_id", ""))  # Sửa 'student_id' -> 'id'
            self.inputStdName.setText(student_data.get("full_name", ""))  # Sửa 'full_name' -> 'name'
            self.inputFaculty.setText(student_data.get("faculty", ""))  # Sửa 'faculty_name' -> 'faculty' và dùng setText
            self.inputMajor.setText(student_data.get("major", ""))  # Sửa 'major_name' -> 'major' và dùng setText
            self.inputClassroom.setText(student_data.get("class_name", ""))  # Giữ nguyên

            # self.okBtn.clicked.connect(self.buttonController.handle_add)


        elif mode == FormMode.EDIT:
            self.labelForm.setText("Edit Student Information")
            self.okBtn.setIcon(QIcon("../UI/icons/save.svg"))
            self.okBtn.setText(" Save")

            if not student_data:
                print("⚠️ student_data is None")
                self.reject()
                return

            # Load data
            self.student_id_to_edit = student_data.get("student_id")

            self.inputStdID.setText(student_data.get("student_id", ""))  # Sửa 'student_id' -> 'id'
            self.inputStdName.setText(student_data.get("full_name", ""))  # Sửa 'full_name' -> 'name'
            self.inputFaculty.setText(student_data.get("faculty", ""))  # Sửa 'faculty_name' -> 'faculty' và dùng setText
            self.inputMajor.setText(student_data.get("major", ""))  # Sửa 'major_name' -> 'major' và dùng setText
            self.inputClassroom.setText(student_data.get("class_name", ""))  # Giữ nguyên
            self.inputMidtermScore.setText(student_data.get("midterm_score", ""))
            self.inputFinalScore.setText(student_data.get("final_score", ""))
            self.inputProcessScore.setText(student_data.get("process_score", ""))

        # Gắn sự kiện
        self.okBtn.clicked.connect(self.controller.handle_save)

    def get_form_data(self):
        """Trả về dictionary đầy đủ để lưu vào CSDL."""
        return {
            # Lấy các ID đã được lưu lại khi form được tạo
            "student_id": self.student_id_to_edit,
            "class_subject_id": self.class_subject_id,
            "year": self.year,

            # Lấy điểm từ các ô nhập liệu
            "midterm_score": self.inputMidtermScore.text(),
            "final_score": self.inputFinalScore.text(),
            "process_score": self.inputProcessScore.text(),

            # Bạn có thể thêm các thông tin khác nếu cần
            # "full_name": self.inputStdName.text(), # Không cần thiết cho bảng scores
        }

        # Gọi đến QDateEdit trong giao diện
        # self.inputStdDate.setCalendarPopup(True)
        # self.inputStdDate.setDate(QDate.currentDate())
        # Gắn event filter để bắt sự kiện mở/đóng lịch
        # self.inputStdDate.calendarWidget().installEventFilter(self)

        # calendar = self.inputStdDate.calendarWidget()
        # calendar.setStyleSheet("""
        #     QWidget {
        #         background-color: white;
        #         color: black;
        #         font: 10pt "Segoe UI";
        #     }
        #
        #     QToolButton:hover {
        #         background-color: #45a049;
        #     }
        #
        #     QMenu {
        #         background-color: white;
        #         color: black;
        #     }
        #
        #     QSpinBox {
        #         background-color: white;
        #     }
        #
        #     QCalendarWidget QAbstractItemView {
        #         selection-background-color: #0078d7;
        #         selection-color: white;
        #         background-color: #f9f9f9;
        #         gridline-color: #c0c0c0;
        #     }
        #
        #     QCalendarWidget QToolButton#qt_calendar_prevmonth,
        #     QCalendarWidget QToolButton#qt_calendar_nextmonth {
        #         icon-size: 24px 24px;
        #         width: 30px;
        #     }
        # """)

        # buttons = [
        #     self.personal,
        #     self.academic,
        #     self.results,
        # ]
        # index_map = {btn: i for i, btn in enumerate(buttons)}
        #
        # self.menu_nav = MenuNavigator(self.stackedWidget, buttons, index_map, default_button=self.personal)

        # self.studentFormController = StudentFormController(self)

    def eventFilter(self, source, event):
        if source == self.inputStdDate.calendarWidget():
            if event.type() == QEvent.Show:
                # Lấy QSS hiện tại
                style = self.inputStdDate.styleSheet()
                # Thay icon down -> up
                style = style.replace("chevron-down.svg", "chevron-up.svg")
                self.inputStdDate.setStyleSheet(style)

            elif event.type() == QEvent.Hide:
                # Ngược lại khi đóng
                style = self.inputStdDate.styleSheet()
                style = style.replace("chevron-up.svg", "chevron-down.svg")
                self.inputStdDate.setStyleSheet(style)

        return super().eventFilter(source, event)


    # def invisible(self):
    #     # self.setWindowFlags(Qt.FramelessWindowHint)
    #     self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
    #     self.setAttribute(Qt.WA_TranslucentBackground)
    #     self.show()


    def show_error(self, message):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Lỗi", message)