from PyQt5.QtCore import QDate, Qt, QEvent, QObject
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from src.constants.form_mode import FormMode
from src.windows.student.function_window import open_add_edit_student


class StudentListController(QObject):
    def __init__(self, table_widget, parent=None, student_data=None, edit_button=None):
        super().__init__(parent)
        self.tableList = table_widget
        self.parent = parent
        self.editStudentBtn = edit_button  # ✅ GÁN

        if self.editStudentBtn:
            self.editStudentBtn.hide()

        self.tableList.itemSelectionChanged.connect(self.on_row_selected)

        self.tableList.viewport().installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

        self.tableList.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableList.setSelectionMode(QTableWidget.SingleSelection)
        self.tableList.setFocusPolicy(Qt.StrongFocus)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            # Click vùng bên trong table nhưng không có item
            if watched == self.tableList.viewport():
                index = self.tableList.indexAt(event.pos())
                if not index.isValid():
                    self.tableList.clearSelection()
                    if self.editStudentBtn:
                        self.editStudentBtn.hide()

            # 👇 Click bên ngoài bảng
            elif watched == self.parent:
                # Nếu vùng click không nằm trong table
                global_pos = event.globalPos()
                table_rect = self.tableList.geometry()
                table_pos = self.tableList.mapToGlobal(table_rect.topLeft())
                table_global_rect = table_rect.translated(table_pos - table_rect.topLeft())

                if not table_global_rect.contains(global_pos):
                    self.tableList.clearSelection()
                    if self.editStudentBtn:
                        self.editStudentBtn.hide()

        return super().eventFilter(watched, event)

    def open_add_student_dialog(self):
        try:
            print("Opening add dialog...")
            new_student = open_add_edit_student(self.parent, FormMode.ADD)
            if new_student:
                self.save_student(new_student)
        except Exception as e:
            print("🔥 Error when opening dialog:", e)

    def open_edit_student_dialog(self, student_data):
        try:
            print("🔍 student_data:", student_data)
            updated_student = open_add_edit_student(self.parent, FormMode.EDIT, student_data)
            if updated_student:
                self.update_student(updated_student)

        except Exception as e:
            print("🔥 Error when opening dialog:", e)

    def save_student(self, new_student):
        from src.models.student import student_model
        student_model.add_student(new_student)
        self.load_students_to_table()

    def update_student(self, updated_student):
        from src.models.student import student_model
        student_model.update_student(updated_student["id"], updated_student)
        self.load_students_to_table()


    def handle_edit_button_clicked(self):
        selected_ranges = self.tableList.selectedRanges()
        if selected_ranges:
            row = selected_ranges[0].topRow()
            student_data = self.get_student_data_from_row(row)
            self.open_edit_student_dialog(student_data)

    def on_row_selected(self):
        print("📌 Row selection changed")
        selected = self.tableList.selectedRanges()
        print("Selected ranges:", selected)
        if self.editStudentBtn:
            self.editStudentBtn.setVisible(bool(selected))

    def get_student_data_from_row(self, row):
        def safe_get_text(column):
            item = self.tableList.item(row, column)
            return item.text() if item else ""

        student_id = safe_get_text(0)
        name = safe_get_text(1)
        gender = safe_get_text(2)
        dob_str = safe_get_text(3)
        dob = QDate.fromString(dob_str, "dd/MM/yyyy") if dob_str else QDate.currentDate()
        email = safe_get_text(4)
        phone = safe_get_text(5)
        address = safe_get_text(6)
        major = safe_get_text(7)
        class_name = safe_get_text(8)
        academic_year = safe_get_text(9)
        enrollment_date_str = safe_get_text(10)
        enrollment_date = QDate.fromString(enrollment_date_str, "dd/MM/yyyy") if enrollment_date_str else QDate.currentDate()
        semester = safe_get_text(11)
        gpa = safe_get_text(12)
        accumulated_credits = safe_get_text(13)
        attendance_rate = safe_get_text(14)
        scholarship_info = safe_get_text(15)

        return {
            "id": student_id,
            "name": name,
            "gender": gender,
            "dob": dob,
            "email": email,
            "phone": phone,
            "address": address,
            "major": major,
            "class_name": class_name,
            "academic_year": academic_year,
            "enrollment_date": enrollment_date,
            "semester": semester,
            "gpa": gpa,
            "accumulated_credits": accumulated_credits,
            "attendance_rate": attendance_rate,
            "scholarship_info": scholarship_info

        }

    def load_students_to_table(self):
        from src.models.student import student_model
        students = student_model.get_all_students()

        print("📌 students:", students)

        self.tableList.setRowCount(0)

        for row_idx, student in enumerate(students):
            self.tableList.insertRow(row_idx)
            for col_idx, value in enumerate(student):
                item = QTableWidgetItem(str(value))
                self.tableList.setItem(row_idx, col_idx, item)









