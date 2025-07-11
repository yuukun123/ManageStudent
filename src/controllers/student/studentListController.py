from PyQt5.QtCore import QDate, Qt, QEvent, QObject
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox

from src.models.student.student_model import get_students_by_class_ids
from src.components.student_filters import setup_faculty_filter, setup_classroom_filter
from src.components.filter_utils import filter_students_by_keyword, sort_students_by_name
from src.constants.table_headers import STUDENT_TABLE_HEADERS

class StudentListController(QObject):
    def __init__(self, table_widget, parent=None, student_page=None):
        super().__init__(parent)
        self.studentList = table_widget
        self.parent = parent
        self.student_page = student_page
        self._setup_table_header()

        self._teacher_context = None
        self._initialized_for_user = False
        self._is_loading = False

        self.filterFacultyStudent = self.parent.filterFacultyStudent
        self.filterClassroomStudent = self.parent.filterClassroomStudent

        self._setup_table_behavior()
        self._connect_signals()

        self.searchInput = self.parent.search
        self.searchButton = self.parent.searchStdBtn

        self.searchButton.clicked.connect(self.update_student_table)

    def _setup_table_behavior(self):
        self.studentList.setSelectionBehavior(QTableWidget.SelectRows)
        self.studentList.setSelectionMode(QTableWidget.SingleSelection)
        self.studentList.setFocusPolicy(Qt.StrongFocus)
        self.studentList.viewport().installEventFilter(self)
        if self.parent:
            self.parent.installEventFilter(self)

    def _connect_signals(self):
        self.studentList.itemSelectionChanged.connect(self.on_row_selected)
        self.filterFacultyStudent.currentIndexChanged.connect(self.on_faculty_changed)
        self.filterClassroomStudent.currentIndexChanged.connect(self.update_student_table)
        self.parent.search.textChanged.connect(self.update_student_table)
        self.parent.filterStudentCB.currentIndexChanged.connect(self.update_student_table)

    def setup_for_user(self, teacher_context=None):
        if self._initialized_for_user and self._teacher_context == teacher_context:
            return

        self._teacher_context = teacher_context

        if teacher_context is None:
            print("❌ Không có thông tin phân quyền cho giáo viên.")
            QMessageBox.critical(self.parent, "Lỗi phân quyền", "Tài khoản hiện tại chưa được phân công lớp học.")
            return

        print("Setting up view for: Teacher")

        self._is_loading = True
        self.setup_faculty_filter()
        self._is_loading = False

        self.update_student_table()
        self._initialized_for_user = True

    def _setup_table_header(self):
        self.studentList.setColumnCount(len(STUDENT_TABLE_HEADERS))
        self.studentList.setHorizontalHeaderLabels(STUDENT_TABLE_HEADERS)

        self.studentList.horizontalHeader().setVisible(True)
        self.studentList.verticalHeader().setVisible(True)

        fixed_width = 200
        for col in range(len(STUDENT_TABLE_HEADERS)):
            self.studentList.setColumnWidth(col, fixed_width)

    def setup_faculty_filter(self):
        print("🧪 Thiết lập bộ lọc KHOA...")
        setup_faculty_filter(self.filterFacultyStudent, self._teacher_context)
        self.setup_classroom_filter()

    def setup_classroom_filter(self):
        print("🧪 Thiết lập bộ lọc LỚP...")
        faculty_id = self.filterFacultyStudent.currentData()
        setup_classroom_filter(self.filterClassroomStudent, faculty_id, self._teacher_context)

        if faculty_id == -1:
            print("✅ Gọi lại update_student_table vì chọn All faculty")
            self.update_student_table()

    def on_faculty_changed(self):
        if self._is_loading:
            return

        print("⚙️ User changed faculty -> Cập nhật danh sách LỚP")
        self.setup_classroom_filter()

    def update_student_table(self):
        if self._is_loading:
            return

        print("⚙️ update_student_table() -> Cập nhật BẢNG DỮ LIỆU")
        faculty_id = self.filterFacultyStudent.currentData()
        class_id = self.filterClassroomStudent.currentData()
        keyword = self.parent.search.text().strip().lower()
        sort_order = self.parent.filterStudentCB.currentText()
        print(f"--> Filtering with Faculty ID: {faculty_id}, Class ID: {class_id}, Keyword: '{keyword}'")

        all_allowed_students = []
        if self._teacher_context:
            allowed_classes = self._teacher_context.get('classes', [])
            if allowed_classes:
                allowed_class_ids = [c[0] for c in allowed_classes]
                all_allowed_students = get_students_by_class_ids(allowed_class_ids)

        filtered_list = all_allowed_students
        if faculty_id != -1:
            filtered_list = [s for s in filtered_list if s.get('faculty_id') == faculty_id]
        if class_id != -1:
            filtered_list = [s for s in filtered_list if s.get('class_id') == class_id]

        filtered_list = filter_students_by_keyword(filtered_list, keyword)

        if sort_order in ["sort A - Z", "sort Z - A"]:
            filtered_list = sort_students_by_name(filtered_list, sort_order)

        self.populate_table(filtered_list)

    def populate_table(self, students):
        self.studentList.setRowCount(0)
        for row_idx, student in enumerate(students):
            self.studentList.insertRow(row_idx)
            values = [
                student.get("student_id", ""), student.get("full_name", ""), student.get("gender", ""),
                student.get("date_of_birth", ""), student.get("email", ""), student.get("phone_number", ""),
                student.get("address", ""), student.get("faculty_name", ""), student.get("major_name", ""),
                student.get("class_name", ""), str(student.get("academic_year", "")),
                str(student.get("enrollment_year", "")), str(student.get("semester_name", "")),
                str(student.get("gpa", "")), str(student.get("accumulated_credits", "")),
                str(student.get("attendance_rate", "")), str(student.get("scholarship_info", ""))
            ]
            for col_idx, value in enumerate(values):
                self.studentList.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def on_row_selected(self):
        print("📌 Row selection changed")
        selected = self.studentList.selectedRanges()
        print("Selected ranges:", selected)
