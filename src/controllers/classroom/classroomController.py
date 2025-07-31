from PyQt5.QtChart import QChart, QPieSeries
from PyQt5.QtCore import QDate, Qt, QEvent, QObject
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView

from src.models.student.student_model import get_classroom_kpis, get_all_academic_years, get_all_semesters, get_class_summary_stats, get_scores_for_histogram, get_start_year_from_academic_id
from src.components.student_filters import setup_faculty_filter, setup_classroom_filter
from src.components.filter_utils import filter_students_by_keyword, sort_students_by_name
from src.constants.table_headers import CLASSROOM_SUMMARY_HEADERS_EN_SHORT


class ClassroomController(QObject):
    def __init__(self, table_widget, parent = None):
    # def __init__(self, parent=None):
        super().__init__(parent)
        self.summaryTable = table_widget
        self.parent = parent
        # self.classroom_page = classroom_page
        # self._setup_table_header()

        self._teacher_context = None
        self._initialized_for_user = False
        self._is_loading = False

        self.filterAcademicYear = self.parent.filterAcademicYear
        self.filterSemester = self.parent.filterSemester

        # Các QLabel cho thẻ KPI trong area1
        # Thay thế bằng objectName chính xác của bạn
        self.kpi_class_count_label = self.parent.kpiValueLabel1
        self.kpi_student_count_label = self.parent.kpiValueLabel2
        self.kpi_pass_rate_label = self.parent.kpiValueLabel3

        # Bảng và Biểu đồ
        self.summaryTable = self.parent.area2
        self.detailChart = self.parent.area3  # QChartparent

        self.summary_table_data = []

        # self._setup_table_behavior()
        self._connect_signals()
        self._populate_academic_year_filter()
        self._populate_semester_filter()
        self._setup_summary_table()

        # self.searchInput = self.parent.search
        # self.searchButton = self.parent.searchStdBtn
        #
        # self.searchButton.clicked.connect(self.update_student_table)

    def _connect_signals(self):
        # self.summaryTable.itemSelectionChanged.connect(self.on_summary_table_row_clicked)
        self.summaryTable.cellClicked.connect(self.on_summary_table_row_clicked)  # Dùng cellClicked
        self.filterAcademicYear.currentIndexChanged.connect(self.update_all_components)
        self.filterSemester.currentIndexChanged.connect(self.update_all_components)

        # self.parent.search.textChanged.connect(self.update_student_table)
        # self.parent.filterStudentCB.currentIndexChanged.connect(self.update_student_table)

    def _setup_summary_table(self):
        """Thiết lập các thuộc tính và tiêu đề cho bảng so sánh."""
        self.summaryTable.setColumnCount(len(CLASSROOM_SUMMARY_HEADERS_EN_SHORT))
        self.summaryTable.setHorizontalHeaderLabels(CLASSROOM_SUMMARY_HEADERS_EN_SHORT)

        # Các thiết lập giao diện khác
        self.summaryTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.summaryTable.setSelectionMode(QTableWidget.SingleSelection)
        self.summaryTable.setEditTriggers(QTableWidget.NoEditTriggers)  # Không cho phép sửa trực tiếp
        self.summaryTable.verticalHeader().setVisible(False)  # Ẩn cột số thứ tự mặc định

        header = self.summaryTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Cho cột "Class Section" giãn ra
        for i in range(1, self.summaryTable.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    # def _setup_table_behavior(self):
    #     self.summaryTable.setSelectionBehavior(QTableWidget.SelectRows)
    #     self.summaryTable.setSelectionMode(QTableWidget.SingleSelection)
    #     self.summaryTable.setFocusPolicy(Qt.StrongFocus)
    #     self.summaryTable.parentport().installEventFilter(self)
    #     if self.parent:
    #         self.parent.installEventFilter(self)
    #
    # def _setup_table_header(self):
    #     self.summaryTable.setColumnCount(len(CLASSROOM_SUMMARY_HEADERS_EN_SHORT))
    #     self.summaryTable.setHorizontalHeaderLabels(CLASSROOM_SUMMARY_HEADERS_EN_SHORT)
    #
    #     self.summaryTable.horizontalHeader().setVisible(True)
    #     self.summaryTable.verticalHeader().setVisible(True)
    #
    #     fixed_width = 200
    #     for col in range(len(CLASSROOM_SUMMARY_HEADERS_EN_SHORT)):
    #         self.summaryTable.setColumnWidth(col, fixed_width)

    def setup_for_user(self, teacher_context=None):
        if self._initialized_for_user and self._teacher_context == teacher_context:
            return

        self._teacher_context = teacher_context
        self._initialized_for_user = True

        if teacher_context is None:
            print("❌ Không có thông tin phân quyền cho giáo viên.")
            QMessageBox.critical(self.parent, "Lỗi phân quyền", "Tài khoản hiện tại chưa được phân công lớp học.")
            return

        print("Setting up parent for: Teacher")

        self._is_loading = True
        self._populate_academic_year_filter()
        self._populate_semester_filter()

        self._is_loading = False

        self.update_all_components()

        # self.update_student_table()

    def _populate_academic_year_filter(self):
        """Điền dữ liệu vào ComboBox lọc năm học."""
        self.filterAcademicYear.clear()
        all_years = get_all_academic_years()
        if not all_years:
            return

        for year in all_years:
            display_text = f"{year['start_year']} - {year['end_year']}"
            # Quan trọng: Hiển thị text dễ đọc, nhưng lưu trữ ID để dùng cho truy vấn
            self.filterAcademicYear.addItem(display_text, userData=year['academic_year_id'])

    def _populate_semester_filter(self):
        """Điền dữ liệu vào ComboBox lọc học kiềm."""
        self.filterSemester.clear()
        all_semesters = get_all_semesters()
        if not all_semesters:
            return

        for semester in all_semesters:
            self.filterSemester.addItem(semester['semester_name'], userData=semester['semester_id'])

    def update_all_components(self):
        if self._is_loading:
            return

        if not self._teacher_context or not self._initialized_for_user:
            return

        """Hàm chính để cập nhật toàn bộ trang Classroom."""
        print("🔄 Updating Classroom page...")
        self.update_kpi_cards()
        self.update_summary_table() # Sẽ làm ở bước sau
        self.clear_detail_chart()   # Sẽ làm ở bước sau

    def clear_detail_chart(self):
        """Xóa biểu đồ chi tiết và hiển thị thông báo."""
        if self.detailChart.chart():
            self.detailChart.chart().removeAllSeries()
            # Hoặc bạn có thể hiển thị một QLabel thông báo ở đây
            # self.detailChart.setChart(None) -> Cách này cũng xóa chart

    def update_kpi_cards(self):

        """Cập nhật dữ liệu cho các thẻ KPI trong area1."""
        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id]:
            return

        # Gọi hàm model
        kpi_data = get_classroom_kpis(teacher_id, academic_year_id, semester_id)

        # Cập nhật giao diện
        if kpi_data:
            self.kpi_class_count_label.setText(str(kpi_data.get('total_classes', 0)))
            self.kpi_student_count_label.setText(str(kpi_data.get('total_students', 0)))

            pass_rate = kpi_data.get('pass_rate', 0)
            self.kpi_pass_rate_label.setText(f"{pass_rate:.1f}%" if pass_rate is not None else "N/A")
        else:
            # Reset về 0 nếu không có dữ liệu
            self.kpi_class_count_label.setText("0")
            self.kpi_student_count_label.setText("0")
            self.kpi_pass_rate_label.setText("N/A")

    def update_summary_table(self):
        """Lấy và điền dữ liệu vào bảng so sánh các lớp."""
        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id]:
            self.summaryTable.setRowCount(0)  # Xóa bảng nếu thiếu bộ lọc
            return

        # Gọi hàm model mới
        summary_data = get_class_summary_stats(teacher_id, academic_year_id, semester_id)

        self.summary_table_data = summary_data

        self.summaryTable.setRowCount(0)  # Xóa dữ liệu cũ
        if not summary_data:
            return

        for row_idx, row_data in enumerate(summary_data):
            self.summaryTable.insertRow(row_idx)

            # Định dạng dữ liệu trước khi hiển thị
            pass_rate = row_data.get('pass_rate')

            # Tạo các item cho mỗi ô
            items = [
                QTableWidgetItem(str(row_data.get('section_name', 'N/A'))),
                QTableWidgetItem(str(row_data.get('student_count', 0))),
                QTableWidgetItem(f"{row_data.get('avg_process_score', 0):.2f}"),
                QTableWidgetItem(f"{row_data.get('avg_final_score', 0):.2f}"),
                QTableWidgetItem(f"{pass_rate:.1f}%" if pass_rate is not None else "N/A"),
                QTableWidgetItem(str(row_data.get('excellent_students', 0))),
                QTableWidgetItem(str(row_data.get('failed_students', 0)))
            ]

            # Căn giữa các cột số
            for i in range(1, len(items)):
                items[i].setTextAlignment(Qt.AlignCenter)

            # Điền các item vào bảng
            for col_idx, item in enumerate(items):
                self.summaryTable.setItem(row_idx, col_idx, item)

    def on_summary_table_row_clicked(self, row, column):
        """
        Khi người dùng click vào một dòng, lấy class_subject_id và gọi hàm vẽ biểu đồ.
        """
        print(f"Row {row} clicked. Updating detail chart.")
        if row < len(self.summary_table_data):
            # Lấy dữ liệu của dòng được click từ danh sách đã lưu
            clicked_class_data = self.summary_table_data[row]
            class_subject_id = clicked_class_data.get('class_subject_id')
            class_name = clicked_class_data.get('section_name')

            # Gọi hàm vẽ biểu đồ chi tiết
            self.update_detail_chart(class_subject_id, class_name)

    def update_detail_chart(self, class_subject_id, class_name):
        """
        Vẽ biểu đồ Phân loại Học lực (Pie Chart) cho lớp được chọn.
        """
        academic_year_id = self.filterAcademicYear.currentData()
        year = get_start_year_from_academic_id(academic_year_id)

        if None in [class_subject_id, year]:
            # Xóa biểu đồ cũ nếu không có đủ thông tin
            if self.detailChart.chart(): self.detailChart.chart().removeAllSeries()
            return

        # Lấy danh sách điểm của lớp
        scores = get_scores_for_histogram(class_subject_id, year)

        if not scores:
            # Có thể hiển thị thông báo "Lớp chưa có điểm"
            if self.detailChart.chart(): self.detailChart.chart().removeAllSeries()
            return

        # TÍNH TOÁN PHÂN LOẠI HỌC LỰC
        grade_counts = {'Giỏi (A)': 0, 'Khá (B)': 0, 'Trung bình (C)': 0, 'Yếu/Kém (D/F)': 0}
        for score in scores:
            if score >= 8.5:
                grade_counts['Giỏi (A)'] += 1
            elif score >= 7.0:
                grade_counts['Khá (B)'] += 1
            elif score >= 5.5:
                grade_counts['Trung bình (C)'] += 1
            else:
                grade_counts['Yếu/Kém (D/F)'] += 1

        # VẼ BIỂU ĐỒ TRÒN (PIE CHART)
        series = QPieSeries()
        total_students = len(scores)

        for grade, count in grade_counts.items():
            if count > 0:
                # Tạo một "miếng bánh"
                slice_ = series.append(f"{grade}: {count} SV", count)
                # Tính phần trăm để hiển thị trên nhãn
                percent = (count / total_students) * 100
                slice_.setLabel(f"{slice_.label()} ({percent:.1f}%)")

        series.setLabelsVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Phân loại Học lực - Lớp: {class_name}")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.legend().setAlignment(Qt.AlignRight)

        self.detailChart.setChart(chart)
        self.detailChart.setRenderHint(QPainter.Antialiasing)

    # def update_student_table(self):
    #     if self._is_loading:
    #         return
    #
    #     if not self._teacher_context:
    #         print("  -> Info: No teacher context available. Clearing table.")
    #         self.populate_table([])
    #         return
    #
    #     print("\n🔄 Updating student list based on assignments...")
    #
    #     print("⚙️ update_student_table() -> Cập nhật BẢNG DỮ LIỆU")
    #     teacher_id = self._teacher_context.get('teacher_id')
    #     faculty_id = self.filterFacultyStudent.currentData()
    #     class_id = self.filterClassroomStudent.currentData()
    #     academic_year_id = self.filterAcademicYearStudent.currentData()
    #     semester_id = self.filterSemesterStudent.currentData()
    #     keyword = self.parent.search.text().strip().lower()
    #     sort_order = self.parent.filterStudentCB.currentText()
    #     print(f"--> Filtering with Faculty ID: {faculty_id}, Class ID: {class_id}, Keyword: '{keyword}'")
    #
    #     # 2. Kiểm tra các giá trị bắt buộc
    #     # Giáo viên phải được phân công trong một năm học và học kỳ cụ thể
    #     if None in [teacher_id, academic_year_id, semester_id]:
    #         print("  -> Info: Teacher, Academic Year, or Semester not selected. Clearing table.")
    #         self.populate_table([])
    #         return
    #
    #     print(f"--> Filtering with: AY_ID={academic_year_id}, Sem_ID={semester_id}, Class_ID={class_id}")


        # # 3. Gọi hàm model mới để lấy danh sách sinh viên được phân công
        # student_list = get_assigned_students_for_teacher(
        #     teacher_id=teacher_id,
        #     academic_year_id=academic_year_id,
        #     semester_id=semester_id,
        #     class_id=class_id,
        #     faculty_id=faculty_id
        # )
        # filtered_list = student_list
        # # filtered_list = filter_students_by_keyword(filtered_list, keyword)
        # if keyword:
        #     filtered_list = filter_students_by_keyword(filtered_list, keyword)
        #
        # if sort_order in ["sort A - Z", "sort Z - A"]:
        #     filtered_list = sort_students_by_name(filtered_list, sort_order)
        #
        # self.populate_table(filtered_list)

    # def populate_table(self, students):
    #     self.area2.setRowCount(0)
    #     for row_idx, student in enumerate(students):
    #         self.area2.insertRow(row_idx)
    #         values = [
    #             student.get("student_id", ""), student.get("full_name", ""), student.get("gender", ""),
    #             student.get("date_of_birth", ""), student.get("email", ""), student.get("phone_number", ""),
    #             student.get("address", ""), student.get("faculty_name", ""), student.get("major_name", ""),
    #             student.get("class_name", ""), str(student.get("academic_year", "")),
    #             str(student.get("enrollment_year", "")), str(student.get("semester_name", "")),
    #             str(student.get("gpa", "")), str(student.get("accumulated_credits", "")),
    #             str(student.get("attendance_rate", "")), str(student.get("scholarship_info", ""))
    #         ]
    #         for col_idx, value in enumerate(values):
    #             self.area2.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    #
    # def on_row_selected(self):
    #     print("📌 Row selection changed")
    #     selected = self.area2.selectedRanges()
    #     print("Selected ranges:", selected)

