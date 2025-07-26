from PyQt5.QtCore import QDate, Qt, QEvent, QObject
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLabel

from src.constants.form_mode import FormMode
from src.windows.student.function_window import open_add_edit_student_score
from src.models.student.student_model import (
    get_student_scores_for_subject, get_subjects_by_teacher_and_classes, get_all_academic_years, get_class_subject_id, get_start_year_from_academic_id, get_all_semesters
)
from src.components.student_filters import setup_faculty_filter, setup_classroom_filter
from src.components.filter_utils import filter_students_by_keyword, sort_students_by_name
from src.constants.table_headers import SCORE_TABLE_HEADERS


class StudentScoreController(QObject):
    def __init__(self, table_widget, parent=None, edit_button=None, score_page=None):
        super().__init__(parent)
        self.scoresList = table_widget
        self.parent = parent
        self.editScoreBtn = edit_button
        self.score_page = score_page

        # Gán các widget từ parent
        self.filterFacultyScore = self.parent.filterFacultyScore
        self.filterClassroomScore = self.parent.filterClassroomScore
        self.filterAcademicYearScore = self.parent.filterAcademicYearScore
        self.filterSemesterScore = self.parent.filterSemesterScore
        # Đây là một QLabel, không phải ComboBox
        self.subjectLabel = self.parent.filterSubjectScore
        self.searchInput = self.parent.searchName
        self.searchButton = self.parent.searchStdBtn_2
        self.sortComboBox = self.parent.filterScoreCB


        self._teacher_context = None
        self._initialized_for_user = False
        self._is_loading = False
        self.current_subject_id = None
        self.current_class_subject_id = None
        self.current_year = None

        self._setup_table_header()
        self._setup_table_behavior()
        self._connect_signals()
        self._populate_academic_year_filter()
        self._populate_semester_filter()

    def _setup_table_behavior(self):
        self.scoresList.setSelectionBehavior(QTableWidget.SelectRows)
        self.scoresList.setSelectionMode(QTableWidget.SingleSelection)
        self.scoresList.setFocusPolicy(Qt.StrongFocus)
        self.scoresList.viewport().installEventFilter(self)
        if self.parent:
            self.parent.installEventFilter(self)

    def _setup_table_header(self):
        self.scoresList.setColumnCount(len(SCORE_TABLE_HEADERS))
        self.scoresList.setHorizontalHeaderLabels(SCORE_TABLE_HEADERS)

        self.scoresList.horizontalHeader().setVisible(True)
        self.scoresList.verticalHeader().setVisible(True)

        fixed_width = 230
        for col in range(len(SCORE_TABLE_HEADERS)):
            self.scoresList.setColumnWidth(col, fixed_width)

    def _connect_signals(self):
        """Kết nối tín hiệu với các hàm xử lý."""
        self.filterFacultyScore.currentIndexChanged.connect(self.on_faculty_filter_changed)
        self.filterClassroomScore.currentIndexChanged.connect(self.update_student_table)
        self.filterAcademicYearScore.currentIndexChanged.connect(self.update_student_table)
        self.filterSemesterScore.currentIndexChanged.connect(self.update_student_table)
        # Các tín hiệu khác vẫn giữ nguyên
        self.searchInput.textChanged.connect(self.update_student_table)
        self.searchButton.clicked.connect(self.update_student_table)
        self.sortComboBox.currentIndexChanged.connect(self.update_student_table)
        self.scoresList.itemSelectionChanged.connect(self.on_row_selected)

    def setup_for_user(self, teacher_context):
        """Hàm khởi tạo chính, được gọi khi có thông tin giáo viên."""
        if self._initialized_for_user:
            return
        if not teacher_context:
            QMessageBox.critical(self.parent, "Lỗi phân quyền", "Không có thông tin phân quyền cho giáo viên.")
            return

        self._teacher_context = teacher_context
        self._initialized_for_user = True
        print("🚀 Setting up view for Teacher on Scores Page...")

        self._is_loading = True
        self.setup_faculty_filter()  # Hàm này sẽ tự động gọi setup_classroom_filter
        self._is_loading = False

        self.update_student_table()  # Gọi lần cuối sau khi setup

    def _populate_academic_year_filter(self):
        """Điền dữ liệu vào ComboBox lọc năm học."""
        self.filterAcademicYearScore.clear()
        all_years = get_all_academic_years()
        if not all_years:
            return

        for year in all_years:
            display_text = f"{year['start_year']} - {year['end_year']}"
            # Quan trọng: Hiển thị text dễ đọc, nhưng lưu trữ ID để dùng cho truy vấn
            self.filterAcademicYearScore.addItem(display_text, userData=year['academic_year_id'])

    def _populate_semester_filter(self):
        """Điền dữ liệu vào ComboBox lọc học kiềm."""
        self.filterSemesterScore.clear()
        all_semesters = get_all_semesters()
        if not all_semesters:
            return

        for semester in all_semesters:
            # display_text = f"{semester['start_semester']} - {semester['end_semester']}"
            # Quan trọng: Hiển thị text dễ đọc, nhưng lưu trữ ID để dùng cho truy vấn
            # self.filterSemesterScore.addItem(display_text, userData=semester['semester_id'])
            self.filterSemesterScore.addItem(semester['semester_name'], userData=semester['semester_id'])

    def setup_faculty_filter(self):
        """Điền dữ liệu vào ComboBox Khoa."""
        print("  -> 1. Populating Faculty filter...")
        setup_faculty_filter(self.filterFacultyScore, self._teacher_context, block_signals=True)
        self.setup_classroom_filter()

    def on_faculty_filter_changed(self):
        """Khi Khoa thay đổi, cập nhật lại bộ lọc Lớp."""
        if self._is_loading: return
        print("⚙️ Faculty changed -> updating classroom filter")
        self.setup_classroom_filter()
        self.setup_classroom_filter()

    def setup_classroom_filter(self):
        print("  -> 2. Populating Classroom filter...")
        faculty_id = self.filterFacultyScore.currentData()
        # Dùng hàm helper đã sửa (không có "All classroom")
        # Vẫn block tín hiệu để tránh gọi update_student_table quá sớm
        setup_classroom_filter(self.filterClassroomScore, faculty_id, self._teacher_context, block_signals=True)

        # Tự động chọn item đầu tiên nếu có
        if self.filterClassroomScore.count() > 0:
            self.filterClassroomScore.setCurrentIndex(0)

    def update_student_table(self):
        try:
            if self._is_loading: return
            print("\n🔄 Updating student score table...")
            if not self._teacher_context: return

            teacher_id = self._teacher_context.get('teacher_id')
            class_id = self.filterClassroomScore.currentData()
            academic_year_id = self.filterAcademicYearScore.currentData()
            semester_id = self.filterSemesterScore.currentData()

            # Thêm một bước kiểm tra an toàn
            if None in [class_id, academic_year_id, semester_id] or class_id == -1:
                self.populate_table([])
                self.subjectLabel.setText("Please select all filters")
                return

            # Logic tự động tìm môn học (giữ nguyên)
            subjects = get_subjects_by_teacher_and_classes(teacher_id, [class_id], academic_year_id, semester_id)
            if not subjects:
                print(f"  -> Info: No subjects for class {class_id}.")
                self.populate_table([])
                self.subjectLabel.setText("Subject: N/A")
                self.current_subject_id = None
                return

            first_subject = subjects[0]
            subject_id_to_query = first_subject["subject_id"]
            semester_id_from_db= first_subject["semester_id"]
            subject_name_to_display = first_subject["subject_name"]
            self.current_subject_id = subject_id_to_query
            self.subjectLabel.setText(f"{subject_name_to_display}")

            self.current_class_subject_id = get_class_subject_id(
                class_id, subject_id_to_query, semester_id_from_db
            )

            self.current_year = get_start_year_from_academic_id(academic_year_id)

            student_scores = get_student_scores_for_subject(
                class_ids=[class_id],
                teacher_id=teacher_id,
                subject_id=subject_id_to_query,
                academic_year_id=academic_year_id
            )

            # Lọc và sắp xếp phía client (nếu có)
            keyword = self.searchInput.text().strip().lower()
            if keyword:
                student_scores = filter_students_by_keyword(student_scores, keyword)

            sort_order = self.sortComboBox.currentText()
            if sort_order in ["sort A - Z", "sort Z - A"]:
                student_scores = sort_students_by_name(student_scores, sort_order)

            self.populate_table(student_scores)
        except Exception as e:

            print("🔥🔥🔥 MỘT LỖI KHÔNG MONG MUỐN ĐÃ XẢY RA TRONG update_student_table! 🔥🔥🔥")

            import traceback

            traceback.print_exc()

    def populate_table(self, students):
        self.scoresList.clearSelection()
        if self.editScoreBtn:
            self.editScoreBtn.hide()
        """Điền dữ liệu vào QTableWidget."""
        self.scoresList.setRowCount(0)
        if not students: return

        for row_idx, student in enumerate(students):
            self.scoresList.insertRow(row_idx)
            values = [
                student.get("student_id"), student.get("full_name"), student.get("faculty_name"),
                student.get("major_name"), student.get("class_name"), student.get("midterm_score"),
                student.get("final_score"), student.get("process_score"),
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem()
                item.setText(str(value) if value is not None else "N/A")
                self.scoresList.setItem(row_idx, col_idx, item)

    def on_row_selected(self):
        print("📌 Row selection changed")
        selected = self.scoresList.selectedRanges()
        print("Selected ranges:", selected)
        if self.editScoreBtn:
            self.editScoreBtn.setVisible(bool(selected))

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            if watched == self.scoresList.viewport():
                index = self.scoresList.indexAt(event.pos())
                if not index.isValid():
                    self.scoresList.clearSelection()
                    if self.editScoreBtn:
                        self.editScoreBtn.hide()

            elif watched == self.parent:
                global_pos = event.globalPos()
                table_rect = self.scoresList.geometry()
                table_pos = self.scoresList.mapToGlobal(table_rect.topLeft())
                table_global_rect = table_rect.translated(table_pos - table_rect.topLeft())

                if not table_global_rect.contains(global_pos):
                    self.scoresList.clearSelection()
                    if self.editScoreBtn:
                        self.editScoreBtn.hide()

        return super().eventFilter(watched, event)

    def open_add_score_dialog(self, student_data):
        try:
            faculty_name = self.filterFacultyScore.currentText()
            class_name = self.filterClassroomScore.currentText()

            if faculty_name == "All faculty":
                QMessageBox.warning(self.parent, "Warning", "Please select a faculty before adding a student.")
                return

            print("Opening add dialog...")
            new_student = open_add_edit_student_score(
                self.parent,FormMode.ADD,
                default_faculty_id=self.filterFacultyScore.currentData(),
                default_class_id=self.filterClassroomScore.currentData(),
                student_data=student_data,
                subject_id = self.current_subject_id,
                class_subject_id = self.current_class_subject_id,  # <-- Mới
                year = self.current_year
            )
            if new_student:
                self.save_student_score(new_student)
        except Exception as e:
            print("🔥 Error when opening dialog:", e)

    def open_edit_dialog(self, student_data):
        try:
            print("🔍 student_data:", student_data)
            # student_data = self.get_student_score_data_from_row()

            if not student_data:
                QMessageBox.information(self.parent, "Thông báo", "Vui lòng chọn một sinh viên để sửa.")
                return

            updated_student = open_add_edit_student_score(
                self.parent,
                FormMode.EDIT,
                student_data = student_data,
                subject_id = self.current_subject_id,
                class_subject_id = self.current_class_subject_id,  # <-- Mới
                year = self.current_year
            )
            if updated_student:
                self.update_student_score(updated_student)

        except Exception as e:
            print("🔥 Error when opening dialog:", e)
            import traceback
            traceback.print_exc()

    def save_student_score(self, new_student):
        from src.models.student import student_model
        student_model.add_score(new_student)
        print("✅ Added student score successfully")
        self.update_student_table()  # Cập nhật lại bảng

    def update_student_score(self, updated_student):
        from src.models.student import student_model
        student_model.update_score(updated_student)
        print("✅ Updated student score successfully")
        self.update_student_table()  # Cập nhật lại bảng

    def handle_add_button_clicked(self):
        selected_ranges = self.scoresList.selectedRanges()
        if selected_ranges:
            row = selected_ranges[0].topRow()
            student_data = self.get_student_score_data_from_row(row)
            self.open_add_score_dialog(student_data)

    def handle_edit_button_clicked(self):
        selected_ranges = self.scoresList.selectedRanges()
        if selected_ranges:
            row = selected_ranges[0].topRow()
            student_data = self.get_student_score_data_from_row(row)
            self.open_edit_dialog(student_data)

    def get_student_score_data_from_row(self, row):
        def safe_get_text(column):
            item = self.scoresList.item(row, column)
            return item.text() if item else ""

        student_id = safe_get_text(0)
        full_name = safe_get_text(1)
        faculty = safe_get_text(2)
        major = safe_get_text(3)
        class_name = safe_get_text(4)
        midterm_score = safe_get_text(5)
        final_score = safe_get_text(6)
        process_score = safe_get_text(7)

        # # Truy xuat thong tin khac
        # gender = safe_get_text(8)
        # dob = safe_get_text(9)
        # email = safe_get_text(10)
        # phone = safe_get_text(11)
        # address = safe_get_text(12)
        # academic_year = safe_get_text(13)
        # enrollment_date = safe_get_text(14)
        # semester = safe_get_text(15)
        # gpa = safe_get_text(16)
        # accumulated_credits = safe_get_text(17)
        # attendance_rate = safe_get_text(18)
        # scholarship_info = safe_get_text(19)

        return {
            "student_id": student_id,
            "full_name": full_name,
            "faculty": faculty,
            "major": major,
            "class_name": class_name,
            "midterm_score": midterm_score,
            "final_score": final_score,
            "process_score": process_score

        }
        # pass