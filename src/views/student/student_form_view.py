from PyQt5 import uic
from PyQt5.QtCore import QDate, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from src.constants.form_mode import FormMode
from src.controllers.buttonController import buttonController
from src.controllers.student.studentFormController import StudentFormController
from src.utils.changeTab import MenuNavigator
from src.views.moveable_window import MoveableWindow


class StudentForm(QDialog, MoveableWindow):
    def __init__(self, parent=None, mode="add", student_data=None):
        super().__init__(parent)
        uic.loadUi("../UI/forms/student_form.ui", self)
        MoveableWindow.__init__(self)
        self.invisible()
        # Tạo controller, truyền self vào
        self.buttonController = buttonController(self)
        # Gán nút
        self.cancelBtn.clicked.connect(self.buttonController.handle_cancel)
        self.controller = StudentFormController(self)

        # Tùy chỉnh giao diện theo mode
        if mode == FormMode.ADD:
            self.labelForm.setText("Add New Student")
            self.okBtn.setText("Ok")

        elif mode == FormMode.EDIT:
            self.labelForm.setText("Edit Student Information")
            self.okBtn.setIcon(QIcon("../UI/icons/save.svg"))
            self.okBtn.setText(" Save")

            if not student_data:
                print("⚠️ student_data is None")
                self.reject()
                return

            # Load data
            self.studentID.setText(student_data["id"])
            self.fullName.setText(student_data["name"])
            self.genderCombo.setCurrentText(student_data["gender"])
            self.dateOfBirth.setDate(student_data["dob"])
            self.email.setText(student_data["email"])
            self.phoneNumber.setText(student_data["phone"])
            self.address.setText(student_data["address"])

        # Gắn sự kiện
        self.okBtn.clicked.connect(self.controller.handle_save)

        # Gọi đến QDateEdit trong giao diện
        self.inputStdDate.setCalendarPopup(True)
        self.inputStdDate.setDate(QDate.currentDate())
        # Gắn event filter để bắt sự kiện mở/đóng lịch
        self.inputStdDate.calendarWidget().installEventFilter(self)

        calendar = self.inputStdDate.calendarWidget()
        calendar.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
                font: 10pt "Segoe UI";
            }

            QToolButton:hover {
                background-color: #45a049;
            }

            QMenu {
                background-color: white;
                color: black;
            }

            QSpinBox {
                background-color: white;
            }

            QCalendarWidget QAbstractItemView {
                selection-background-color: #0078d7;
                selection-color: white;
                background-color: #f9f9f9;
                gridline-color: #c0c0c0;
            }

            QCalendarWidget QToolButton#qt_calendar_prevmonth, 
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                icon-size: 24px 24px;
                width: 30px;
            }
        """)

        buttons = [
            self.personal,
            self.academic,
            self.results,
        ]
        index_map = {btn: i for i, btn in enumerate(buttons)}

        self.menu_nav = MenuNavigator(self.stackedWidget, buttons, index_map, default_button=self.personal)

        self.studentFormController = StudentFormController(self)

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


    def invisible(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()

    def get_form_data(self):
        return {
            "student_id": self.studentID.text(),
            "full_name": self.fullName.text(),
            "email": self.email.text(),
            "phone_number": self.phoneNumber.text(),
            "gender": self.genderCombo.currentText(),
            "date_of_birth": self.dateOfBirth.date().toString("dd/MM/yyyy"),
            "address": self.address.text(),
            "major_id": 1,
            "class_id": 1,
            "academic_year_id": 1

        }

    def show_error(self, message):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Lỗi", message)






