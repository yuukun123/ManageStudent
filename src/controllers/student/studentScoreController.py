from PyQt5.QtCore import QDate, Qt, QEvent, QObject
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLabel

from src.constants.form_mode import FormMode
from src.windows.student.function_window import open_add_edit_student_score
from src.models.student.student_model import get_student_scores_for_subject, get_subjects_by_teacher_and_classes
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
        self._setup_table_header()

        self._teacher_context = None
        self._initialized_for_user = False
        self._is_loading = False

        self.filterFacultyScore = self.parent.filterFacultyScore
        self.filterClassroomScore = self.parent.filterClassroomScore

        self._setup_table_behavior()
        self._connect_signals()

        self.searchInput = self.parent.searchName
        self.searchButton_2 = self.parent.searchStdBtn_2

        self.searchButton_2.clicked.connect(self.update_student_table)

    def _setup_table_behavior(self):
        self.scoresList.setSelectionBehavior(QTableWidget.SelectRows)
        self.scoresList.setSelectionMode(QTableWidget.SingleSelection)
        self.scoresList.setFocusPolicy(Qt.StrongFocus)
        self.scoresList.viewport().installEventFilter(self)
        if self.parent:
            self.parent.installEventFilter(self)

    def _connect_signals(self):
        self.scoresList.itemSelectionChanged.connect(self.on_row_selected)
        self.filterFacultyScore.currentIndexChanged.connect(self.on_faculty_changed)
        self.filterClassroomScore.currentIndexChanged.connect(self.update_student_table)
        self.parent.searchName.textChanged.connect(self.update_student_table)
        self.parent.filterScoreCB.currentIndexChanged.connect(self.update_student_table)

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
        self.scoresList.setColumnCount(len(SCORE_TABLE_HEADERS))
        self.scoresList.setHorizontalHeaderLabels(SCORE_TABLE_HEADERS)

        self.scoresList.horizontalHeader().setVisible(True)
        self.scoresList.verticalHeader().setVisible(True)

        fixed_width = 230
        for col in range(len(SCORE_TABLE_HEADERS)):
            self.scoresList.setColumnWidth(col, fixed_width)

    def update_subject_label(self):
        try:
            if not hasattr(self.parent, 'filterSubjectScore') or not isinstance(self.parent.filterSubjectScore, QLabel):
                print("❌ parent.filterSubjectScore không tồn tại hoặc không phải QLabel.")
                return

            selected_class_id = self.filterClassroomScore.currentData()
            teacher_id = self._teacher_context.get("teacher_id")

            print(f"🔍 Lấy môn học cho class_id: {selected_class_id}, teacher_id: {teacher_id}")

            if selected_class_id == -1:
                self.parent.filterSubjectScore.setText("All classes selected")
                print("📚 Không thể xác định môn học khi chọn tất cả lớp.")
                return

            subjects = get_subjects_by_teacher_and_classes(teacher_id, [selected_class_id])

            if subjects:
                subject_names = ", ".join(sub["subject_name"] for sub in subjects)
                self.parent.filterSubjectScore.setText(f"Subject: {subject_names}")
                print(f"📚 Môn học: {subject_names}")
            else:
                self.parent.filterSubjectScore.setText("Subject: N/A")
                print("📚 Không có môn học.")
        except Exception as e:
            print("⚠️ Lỗi khi lấy tên môn học:", e)
            import traceback
            traceback.print_exc()
            self.parent.filterSubjectScore.setText("Subject: N/A")

    def setup_faculty_filter(self):
        print("🧪 Thiết lập bộ lọc KHOA...")
        setup_faculty_filter(self.filterFacultyScore, self._teacher_context)
        self.setup_classroom_filter()

    def setup_classroom_filter(self):
        print("🧪 Thiết lập bộ lọc LỚP...")
        faculty_id = self.filterFacultyScore.currentData()
        setup_classroom_filter(self.filterClassroomScore, faculty_id, self._teacher_context)

        if faculty_id == -1:
            print("✅ Gọi lại update_student_table vì chọn All faculty")
            self.update_student_table()

        # ✅ Hiển thị môn học nếu chọn 1 lớp cụ thể
        self.update_subject_label()

    def on_faculty_changed(self):
        if self._is_loading:
            return

        print("⚙️ User changed faculty -> Cập nhật danh sách LỚP")
        self.setup_classroom_filter()

    def update_student_table(self):
        if self._is_loading:
            return

        print("⚙️ update_student_table() -> Cập nhật BẢNG DỮ LIỆU")
        faculty_id = self.filterFacultyScore.currentData()
        class_id = self.filterClassroomScore.currentData()
        keyword = self.parent.searchName.text().strip().lower()
        sort_order = self.parent.filterScoreCB.currentText()
        print(f"--> Filtering with Faculty ID: {faculty_id}, Class ID: {class_id}, Keyword: '{keyword}'")

        all_allowed_students = []
        if self._teacher_context:
            teacher_id = self._teacher_context.get('teacher_id')
            allowed_classes = self._teacher_context.get('classes', [])
            if allowed_classes:
                allowed_class_ids = [c[0] for c in allowed_classes]

                # ✅ Lọc lại theo class_id nếu được chọn
                filtered_class_ids = allowed_class_ids
                if class_id != -1:
                    filtered_class_ids = [cid for cid in allowed_class_ids if cid == class_id]

                print("Filtered class ids:", filtered_class_ids)

                # ✅ Lấy subject_id trước khi gọi hàm lấy điểm
                subjects = get_subjects_by_teacher_and_classes(teacher_id, filtered_class_ids)
                if not subjects:
                    print("❌ Không có môn học nào phù hợp với lớp được chọn.")
                    self.populate_table([])  # clear bảng
                    self.update_subject_label()
                    return

                # ✅ Lấy subject đầu tiên
                subject_id = subjects[0]["subject_id"]

                # ✅ Gọi hàm đúng với đủ 3 tham số
                all_allowed_students = get_student_scores_for_subject(filtered_class_ids, teacher_id, subject_id)
                print("Fetched students:", all_allowed_students)

        filtered_list = all_allowed_students
        if faculty_id != -1:
            filtered_list = [s for s in filtered_list if s.get('faculty_id') == faculty_id]
        if class_id != -1:
            filtered_list = [s for s in filtered_list if s.get('class_id') == class_id]

        filtered_list = filter_students_by_keyword(filtered_list, keyword)

        if sort_order in ["sort A - Z", "sort Z - A"]:
            filtered_list = sort_students_by_name(filtered_list, sort_order)

        self.populate_table(filtered_list)

        self.update_subject_label()

    def populate_table(self, students):
        self.scoresList.setRowCount(0)
        for row_idx, student in enumerate(students):
            self.scoresList.insertRow(row_idx)
            values = [
                student.get("student_id", ""), student.get("full_name", ""), student.get("faculty_name", ""),
                student.get("major_name", ""), student.get("class_name", ""), student.get("midterm_score", ""),
                student.get("final_score", ""), student.get("process_score", ""),
            ]
            print("Populating student:", student)
            for col_idx, value in enumerate(values):
                self.scoresList.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

                print(f"🔢 Tổng số dòng: {self.scoresList.rowCount()}")
                self.scoresList.repaint()

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


    # def open_add_student_dialog(self):
    #     try:
    #         faculty_name = self.filterFacultyScore.currentText()
    #         class_name = self.filterClassroomScore.currentText()
    #
    #         if faculty_name == "All faculty" or class_name == "All classroom":
    #             QMessageBox.warning(self.parent, "Warning", "Please select a faculty and a classroom before adding a student.")
    #             return
    #
    #         print("Opening add dialog...")
    #         new_student = open_add_edit_student_score(
    #             self.parent,
    #             FormMode.ADD,
    #             default_faculty_id=self.filterFacultyScore.currentData(),
    #             default_class_id=self.filterClassroomScore.currentData()
    #         )
    #         if new_student:
    #             self.save_student(new_student)
    #     except Exception as e:
    #         print("🔥 Error when opening dialog:", e)
    #
    # def open_edit_student_dialog(self, student_data):
    #     try:
    #         print("🔍 student_data:", student_data)
    #         updated_student = open_add_edit_student_score(self.parent, FormMode.EDIT, student_data)
    #         if updated_student:
    #             self.update_student(updated_student)
    #
    #     except Exception as e:
    #         print("🔥 Error when opening dialog:", e)
    #
    # def save_student(self, new_student):
    #     from src.models.student import student_model
    #     student_model.add_score(new_student)
    #     self.update_student_table()  # Cập nhật lại bảng
    #
    # def update_student(self, updated_student):
    #     from src.models.student import student_model
    #     student_model.update_score(updated_student["id"], updated_student)
    #     self.update_student_table()  # Cập nhật lại bảng
    #
    # def handle_edit_button_clicked(self):
    #     selected_ranges = self.scoresListt.selectedRanges()
    #     if selected_ranges:
    #         row = selected_ranges[0].topRow()
    #         student_data = self.get_student_data_from_row(row)
    #         self.open_edit_student_dialog(student_data)

    # def get_student_data_from_row(self, row):
    #     def safe_get_text(column):
    #         item = self.scoresListt.item(row, column)
    #         return item.text() if item else ""
    #
    #     student_id = safe_get_text(0)
    #     name = safe_get_text(1)
    #     gender = safe_get_text(2)
    #     dob_str = safe_get_text(3)
    #     dob = QDate.fromString(dob_str, "dd/MM/yyyy") if dob_str else QDate.currentDate()
    #     email = safe_get_text(4)
    #     phone = safe_get_text(5)
    #     address = safe_get_text(6)
    #     faculty = safe_get_text(7)
    #     major = safe_get_text(8)
    #     class_name = safe_get_text(9)
    #     academic_year = safe_get_text(10)
    #     enrollment_date_str = safe_get_text(11)
    #     enrollment_date = QDate.fromString(enrollment_date_str, "dd/MM/yyyy") if enrollment_date_str else QDate.currentDate()
    #     semester = safe_get_text(12)
    #     gpa = safe_get_text(13)
    #     accumulated_credits = safe_get_text(14)
    #     attendance_rate = safe_get_text(15)
    #     scholarship_info = safe_get_text(16)
    #
    #     return {
    #         "id": student_id,
    #         "name": name,
    #         "gender": gender,
    #         "dob": dob,
    #         "email": email,
    #         "phone": phone,
    #         "address": address,
    #         "faculty": faculty,
    #         "major": major,
    #         "class_name": class_name,
    #         "academic_year": academic_year,
    #         "enrollment_date": enrollment_date,
    #         "semester": semester,
    #         "gpa": gpa,
    #         "accumulated_credits": accumulated_credits,
    #         "attendance_rate": attendance_rate,
    #         "scholarship_info": scholarship_info
    #     }