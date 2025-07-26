from PyQt5.QtChart import QChart, QChartView, QBoxPlotSeries, QBoxSet, QHorizontalStackedBarSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QStackedBarSeries
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFont, QPainter

from src.models.student.student_model import get_scores_for_boxplot, get_pass_fail_stats, get_avg_scores_by_class, get_scores_for_histogram, get_all_academic_years, get_all_semesters, get_all_classes, get_all_subjects, get_start_year_from_academic_id, get_subjects_for_teacher_in_semester, get_classes_for_subject_in_semester


class dashboardController(QObject):
    def __init__(self, parent=None):  # parent ở đây là MainWindow
        super().__init__(parent)
        self.parent = parent

        # --- KHAI BÁO CÁC WIDGET TỪ MAINWINDOW ---
        # Bộ lọc chung
        self.filterAcademicYear = self.parent.filterAcademicYearDB  # Đặt tên widget trong .ui cho đúng
        self.filterSemester = self.parent.filterSemesterDB

        # Bộ lọc chi tiết
        self.subjectFilterComboBox = self.parent.subjectFilterComboBox
        self.classFilterComboBox = self.parent.classFilterComboBox

        # Các Chart View
        self.boxplotChartView = self.parent.boxplotChartView
        self.passFailChartView = self.parent.passFailChartView
        self.histogramChartView = self.parent.histogramChartView
        self.comparisonChartView = self.parent.comparisonChartView
        # --- KẾT THÚC KHAI BÁO ---

        self._teacher_context = None
        self._initialized_for_user = False
        self._is_loading = False

        # Kết nối các tín hiệu
        self._connect_signals()

    def _connect_signals(self):
        # 1. Bộ lọc chung kích hoạt luồng cập nhật phân cấp
        self.filterAcademicYear.currentIndexChanged.connect(self.on_global_filter_changed)
        self.filterSemester.currentIndexChanged.connect(self.on_global_filter_changed)

        # 2. Bộ lọc Môn học kích hoạt cập nhật Lớp và biểu đồ Box Plot
        self.subjectFilterComboBox.currentIndexChanged.connect(self.on_subject_filter_changed)

        # 3. Bộ lọc Lớp chỉ cập nhật biểu đồ Histogram
        self.classFilterComboBox.currentIndexChanged.connect(self.update_histogram_chart)

    def setup_for_user(self, teacher_context):
        """Hàm này được gọi khi chuyển sang tab Dashboard."""
        if self._initialized_for_user or not teacher_context:
            return

        self._teacher_context = teacher_context
        self._initialized_for_user = True
        self._is_loading = True

        print("🚀 Setting up Dashboard...")
        # Điền dữ liệu cho các bộ lọc (viết các hàm populate này)
        self._populate_academic_year_filter()
        self._populate_semester_filter()
        # self._populate_subject_filter()
        # self._populate_class_filter()

        self._is_loading = False
        # self.update_all_charts()  # Tải tất cả biểu đồ lần đầu
        self.on_global_filter_changed()

    # def update_all_charts(self):
    #     if self._is_loading: return
    #     print("\n🔄 Updating all dashboard charts...")
    #     # ... logic lấy academic_year_id, semester_id ...
    #     # Gọi các hàm update riêng lẻ
    #     self.update_boxplot_chart()
    #     self.update_pass_fail_chart()
    #     self.update_histogram_chart()
    #     self.update_comparison_chart()

    def on_global_filter_changed(self):
        """Khi Năm học hoặc Học kỳ thay đổi."""
        if self._is_loading: return

        print("\n🔄 Global filter changed. Updating dependent filters and charts...")

        # Tạm thời khóa các tín hiệu của bộ lọc con để tránh kích hoạt nhiều lần
        self.subjectFilterComboBox.blockSignals(True)
        self.classFilterComboBox.blockSignals(True)

        # 1. Cập nhật lại danh sách Môn học
        self._populate_subject_filter()

        # 2. Cập nhật các biểu đồ tổng quan
        self.update_pass_fail_chart()
        self.update_comparison_chart()

        # Mở lại tín hiệu
        self.subjectFilterComboBox.blockSignals(False)
        self.classFilterComboBox.blockSignals(False)

        # 3. Tự động kích hoạt sự thay đổi của bộ lọc Môn học
        # để cập nhật các thành phần phụ thuộc vào nó
        self.on_subject_filter_changed()

    def on_subject_filter_changed(self):
        """Khi Môn học thay đổi."""
        if self._is_loading: return
        print("  -> Subject filter changed. Updating class filter and box plot...")

        subject_id = self.subjectFilterComboBox.currentData()

        # Khóa tín hiệu của bộ lọc lớp
        self.classFilterComboBox.blockSignals(True)

        # 1. Cập nhật lại danh sách Lớp học phần cho môn này
        self._populate_class_filter(subject_id)

        # Mở lại tín hiệu
        self.classFilterComboBox.blockSignals(False)

        # 2. Cập nhật biểu đồ Box Plot
        self.update_boxplot_chart()

        # 3. Tự động kích hoạt cập nhật Histogram cho lớp đầu tiên
        self.update_histogram_chart()

    #
    def update_boxplot_chart(self):
        """
        Hàm điều phối: Quyết định vẽ Box Plot (nếu có nhiều lớp)
        hoặc Histogram (nếu chỉ có 1 lớp).
        """
        # 1. Lấy giá trị từ bộ lọc
        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()
        subject_id = self.subjectFilterComboBox.currentData()

        # Kiểm tra các ID cần thiết
        if None in [teacher_id, academic_year_id, semester_id, subject_id]:
            if self.boxplotChartView.chart(): self.boxplotChartView.chart().removeAllSeries()
            return

        # 2. Gọi model để lấy dữ liệu điểm
        scores_data = get_scores_for_boxplot(teacher_id, academic_year_id, semester_id, subject_id)

        # 3. Xử lý và nhóm dữ liệu theo lớp
        scores_by_class = {}
        for row in scores_data:
            class_name = row['class_name']
            score = row['final_score']
            if class_name not in scores_by_class:
                scores_by_class[class_name] = []
            scores_by_class[class_name].append(score)

        # 4. Logic quyết định vẽ biểu đồ nào
        if len(scores_by_class) > 1:
            # Nếu có nhiều hơn 1 lớp, vẽ Box Plot để so sánh
            print(" -> Drawing Box Plot for multiple classes...")
            self._draw_boxplot_on_view(self.boxplotChartView, scores_by_class)

        elif len(scores_by_class) == 1:
            # Nếu chỉ có 1 lớp, vẽ Histogram để phân tích sâu lớp đó
            print(" -> Only one class found. Switching to Histogram...")
            class_name = list(scores_by_class.keys())[0]
            scores = scores_by_class[class_name]
            self._draw_histogram_on_view(self.boxplotChartView, scores, class_name)

        else:
            # Nếu không có dữ liệu, xóa biểu đồ
            print(" -> No data for subject comparison chart.")
            if self.boxplotChartView.chart():
                self.boxplotChartView.chart().removeAllSeries()

    def _draw_boxplot_on_view(self, chart_view, scores_by_class):
        """Hàm chuyên vẽ biểu đồ Box Plot lên một QChartView được chỉ định."""
        series = QBoxPlotSeries()
        categories = []

        for class_name, scores in scores_by_class.items():
            if len(scores) < 4: continue  # Bỏ qua lớp không đủ dữ liệu
            scores.sort()
            count = len(scores)

            lower_quartile = scores[int(count * 0.25)]
            median = scores[int(count * 0.5)]
            upper_quartile = scores[int(count * 0.75)]

            box_values = [scores[0], lower_quartile, median, upper_quartile, scores[-1]]
            box_set = QBoxSet(label=class_name)
            box_set.append(box_values)
            series.append(box_set)
            categories.append(class_name)

        if not categories:
            if chart_view.chart(): chart_view.chart().removeAllSeries()
            return

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"So sánh phân phối điểm - Môn: {self.subjectFilterComboBox.currentText()}")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.legend().setVisible(False)
        series.setBoxWidth(0.7)

        axisX = QBarCategoryAxis()
        axisX.append(categories)

        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)
        axisY = chart.axisY()
        axisY.setRange(0, 10)
        axisY.setTitleText("Điểm cuối kỳ")

        chart.axisX_ref = axisX
        chart.axisY_ref = axisY
        chart.setAnimationOptions(QChart.NoAnimation)

        try:
            series.hovered.disconnect()
        except TypeError:
            pass
        series.hovered.connect(self.on_boxplot_hovered)

        chart_view.setChart(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

    def _draw_histogram_on_view(self, chart_view, scores, class_name):
        """Hàm chuyên vẽ biểu đồ Histogram lên một QChartView được chỉ định."""
        bins = [0] * 10
        for score in scores:
            if score >= 10:
                bins[9] += 1
            elif score >= 0:
                bin_index = int(score)
                bins[bin_index] += 1

        series = QBarSeries()
        bar_set = QBarSet("Số lượng sinh viên")
        bar_set.append(bins)
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Phân phối điểm chi tiết - Lớp: {class_name}")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.legend().setVisible(False)

        categories = [f"[{i}, {i + 1})" for i in range(9)] + ["[9, 10]"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)

        axisY = QValueAxis()
        max_val = max(bins) if bins else 0
        axisY.setRange(0, max_val + 1)
        axisY.setTitleText("Số lượng sinh viên")
        axisY.setLabelFormat("%d")

        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)
        chart.setAxisY(axisY, series)

        chart.axisX_ref = axisX
        chart.axisY_ref = axisY
        chart.setAnimationOptions(QChart.NoAnimation)

        chart_view.setChart(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

    #
    def update_pass_fail_chart(self):
        # 1. & 2. Lấy dữ liệu (giữ nguyên)
        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id]:
            if self.passFailChartView.chart(): self.passFailChartView.chart().removeAllSeries()
            return

        stats = get_pass_fail_stats(teacher_id, academic_year_id, semester_id)

        if not stats:
            if self.passFailChartView.chart(): self.passFailChartView.chart().removeAllSeries()
            return

        # --- SỬA ĐỔI SANG BIỂU ĐỒ CỘT ĐỨNG ---
        # 1. Thay đổi loại Series
        series = QStackedBarSeries()  # <-- Bỏ "Horizontal"
        # --- KẾT THÚC THAY ĐỔI 1 ---

        pass_set = QBarSet("Qua môn")
        fail_set = QBarSet("Rớt môn")
        categories = []

        for row in stats:
            total = row['total_students']
            passed = row['passed_students']
            failed = total - passed

            pass_percent = (passed / total) * 100 if total > 0 else 0
            fail_percent = (failed / total) * 100 if total > 0 else 0

            pass_set.append(pass_percent)
            fail_set.append(fail_percent)
            categories.append(row['class_name'])

        series.append(pass_set)
        series.append(fail_set)

        # Biến series này thành biểu đồ 100%
        series.setLabelsVisible(True)  # Hiển thị giá trị % trên cột
        series.setLabelsFormat("@value%")

        chart = QChart()
        chart.addSeries(series)

        chart.setTitle("Tỉ lệ Sinh viên Qua môn theo Lớp học phần")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))

        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignTop)
        legend.setFont(QFont("Segoe UI", 10))

        chart.setAnimationOptions(QChart.NoAnimation)

        # --- SỬA ĐỔI CÁCH CẤU HÌNH TRỤC ---
        # 2. Hoán đổi trục X và Y

        # Trục X (dưới) bây giờ là trục danh mục, chứa TÊN LỚP
        axisX = QBarCategoryAxis()
        axisX.append(categories)

        # Trục Y (trái) bây giờ là trục giá trị, chứa TỈ LỆ %
        axisY = QValueAxis()
        axisY.setRange(0, 100)
        axisY.setTitleText("Tỉ lệ (%)")

        # Thêm trục vào biểu đồ
        chart.addAxis(axisX, Qt.AlignBottom)
        chart.addAxis(axisY, Qt.AlignLeft)

        # Gắn series vào các trục
        series.attachAxis(axisX)
        series.attachAxis(axisY)

        # Giữ tham chiếu
        chart.axisX_ref = axisX
        chart.axisY_ref = axisY
        # --- KẾT THÚC THAY ĐỔI 2 ---

        self.passFailChartView.setChart(chart)
        self.passFailChartView.setRenderHint(QPainter.Antialiasing)

    #
    def update_histogram_chart(self):
        # 1. Lấy giá trị từ bộ lọc
        academic_year_id = self.filterAcademicYear.currentData()
        class_subject_id = self.classFilterComboBox.currentData()

        if None in [academic_year_id, class_subject_id]:
            if self.histogramChartView.chart(): self.histogramChartView.chart().removeAllSeries()
            return

        year = get_start_year_from_academic_id(academic_year_id)
        if year is None:
            if self.histogramChartView.chart(): self.histogramChartView.chart().removeAllSeries()
            return

        # 2. Gọi model
        scores = get_scores_for_histogram(class_subject_id, year)

        # Ngay cả khi không có điểm, vẫn nên vẽ một biểu đồ trống có tiêu đề
        # if not scores:
        #     if self.histogramChartView.chart(): self.histogramChartView.chart().removeAllSeries()
        #     return

        # 3. Xử lý dữ liệu: Chia vào các "bin" (khoảng điểm)
        bins = [0] * 10  # 10 bins: [0,1), [1,2), ..., [9,10]
        for score in scores:
            if score >= 10:
                bins[9] += 1
            elif score >= 0:
                bin_index = int(score)
                bins[bin_index] += 1

        # 4. Tạo Series và điền dữ liệu
        series = QBarSeries()
        bar_set = QBarSet("Số lượng sinh viên")
        bar_set.append(bins)
        series.append(bar_set)

        # --- BƯỚC 5: TẠO VÀ TÙY CHỈNH BIỂU ĐỒ ---
        chart = QChart()
        chart.addSeries(series)

        # 5.1. Thêm Tiêu đề
        class_name = self.classFilterComboBox.currentText()
        chart.setTitle(f"Phân phối điểm cuối kỳ - Lớp: {class_name}")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))

        # 5.2. Cấu hình Chú thích (Legend)
        # Với chỉ một bộ dữ liệu, chú thích có thể không cần thiết, nhưng vẫn nên có
        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignTop)
        legend.setFont(QFont("Segoe UI", 10))

        # 5.3. Tạo và Cấu hình Trục X (Trục danh mục - chứa khoảng điểm)
        categories = [f"[{i}, {i + 1})" for i in range(9)] + ["[9, 10]"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)

        # 5.4. Tạo và Cấu hình Trục Y (Trục giá trị - số lượng SV)
        axisY = QValueAxis()
        # Để thang đo đẹp hơn, làm tròn lên số gần nhất chia hết cho 5
        max_val = max(bins) if bins else 0
        tick_interval = max(1, (max_val // 5) + 1)  # Đảm bảo khoảng chia > 0
        axisY.setTickCount(tick_interval + 1)
        axisY.setRange(0, max_val + 1)
        axisY.setTitleText("Số lượng sinh viên")
        axisY.setLabelFormat("%d")  # Chỉ hiển thị số nguyên

        # 5.5. Gắn các trục vào biểu đồ
        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)
        chart.setAxisY(axisY, series)

        # Giữ tham chiếu để tránh lỗi runtime
        chart.axisX_ref = axisX
        chart.axisY_ref = axisY

        chart.setAnimationOptions(QChart.NoAnimation)

        # --- BƯỚC 6: HIỂN THỊ BIỂU ĐỒ ---
        self.histogramChartView.setChart(chart)
        self.histogramChartView.setRenderHint(QPainter.Antialiasing)

    #
    def update_comparison_chart(self):
        # 1. Lấy giá trị từ bộ lọc
        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id]:
            if self.comparisonChartView.chart(): self.comparisonChartView.chart().removeAllSeries()
            return

        avg_scores_data = get_avg_scores_by_class(teacher_id, academic_year_id, semester_id)

        # Xử lý trường hợp không có dữ liệu
        if not avg_scores_data:
            if self.comparisonChartView.chart(): self.comparisonChartView.chart().removeAllSeries()
            return

        # 2. Tạo Series và điền dữ liệu (giữ nguyên)
        series = QBarSeries()
        process_set = QBarSet("Điểm QT TB")
        final_set = QBarSet("Điểm CK TB")
        categories = []

        for row in avg_scores_data:
            process_set.append(row['avg_process_score'] or 0)
            final_set.append(row['avg_final_score'] or 0)
            categories.append(row['class_name'])

        series.append(process_set)
        series.append(final_set)

        # --- BƯỚC 3: TẠO VÀ TÙY CHỈNH BIỂU ĐỒ (PHẦN NÂNG CẤP) ---
        chart = QChart()
        chart.addSeries(series)

        # 3.1. Thêm Tiêu đề
        chart.setTitle("So sánh Điểm trung bình Quá trình và Cuối kỳ")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))

        # 3.2. Cấu hình Chú thích (Legend)
        legend = chart.legend()
        legend.setVisible(True)
        # --- SỬA LẠI VỊ TRÍ CHÚ THÍCH ---
        legend.setAlignment(Qt.AlignTop)  # Đặt chú thích ở trên cùng
        legend.setFont(QFont("Segoe UI", 10))
        # Để di chuyển nó sang góc phải, bạn có thể cần dùng QGraphicsLayout,
        # nhưng AlignTop thường là đủ tốt cho khởi đầu.

        # 3.3. TẠO TRỤC X VỚI TÊN LỚP (ĐÂY LÀ PHẦN SỬA LỖI CHÍNH)
        axisX = QBarCategoryAxis()
        axisX.append(categories)  # << Đưa danh sách tên lớp vào đây

        # 3.4. TẠO TRỤC Y VỚI THANG ĐIỂM
        axisY = QValueAxis()
        axisY.setRange(0, 10)
        axisY.setTitleText("Điểm trung bình")
        axisY.setLabelFormat("%.1f")

        # 3.5. GẮN CÁC TRỤC VÀO BIỂU ĐỒ (QUAN TRỌNG)
        # Phải gọi createDefaultAxes() TRƯỚC khi set các trục tùy chỉnh
        chart.createDefaultAxes()

        # Ghi đè các trục mặc định bằng các trục đã tùy chỉnh của chúng ta
        chart.setAxisX(axisX, series)
        chart.setAxisY(axisY, series)

        chart.axisX_ref = axisX
        chart.axisY_ref = axisY

        # (Tùy chọn) Ẩn animation để biểu đồ hiện ngay lập tức
        chart.setAnimationOptions(QChart.NoAnimation)

        # --- BƯỚC 4: HIỂN THỊ BIỂU ĐỒ ---
        self.comparisonChartView.setChart(chart)
        # Thêm dòng này để chất lượng hiển thị tốt hơn
        self.comparisonChartView.setRenderHint(QPainter.Antialiasing)

    # bộ lọc
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
            # display_text = f"{semester['start_semester']} - {semester['end_semester']}"
            # Quan trọng: Hiển thị text dễ đọc, nhưng lưu trữ ID để dùng cho truy vấn
            # self.filterSemester.addItem(display_text, userData=semester['semester_id'])
            self.filterSemester.addItem(semester['semester_name'], userData=semester['semester_id'])

    # trong dashboardController.py

    # SỬA LẠI HÀM NÀY
    def _populate_subject_filter(self):
        """
        Điền dữ liệu vào bộ lọc Môn học DỰA TRÊN các bộ lọc chung.
        """
        self.subjectFilterComboBox.clear()

        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id]:
            return

        # Bạn cần một hàm model mới: lấy tất cả môn mà GV dạy trong kỳ đó
        # Hàm này có thể dựa trên get_subjects_by_teacher_and_classes nhưng bỏ lọc class_ids
        subjects = get_subjects_for_teacher_in_semester(teacher_id, academic_year_id, semester_id)
        for subject in subjects:
            self.subjectFilterComboBox.addItem(subject['subject_name'], userData=subject['subject_id'])

    # SỬA LẠI HÀM NÀY
    def _populate_class_filter(self, subject_id):
        """
        Điền dữ liệu vào bộ lọc Lớp DỰA TRÊN Môn học đã chọn.
        """
        self.classFilterComboBox.clear()

        teacher_id = self._teacher_context.get('teacher_id')
        academic_year_id = self.filterAcademicYear.currentData()
        semester_id = self.filterSemester.currentData()

        if None in [teacher_id, academic_year_id, semester_id, subject_id]:
            return

        # Bạn cần hàm model mới: lấy các lớp mà GV dạy MỘT môn cụ thể trong kỳ
        classes = get_classes_for_subject_in_semester(teacher_id, academic_year_id, semester_id, subject_id)

        for cls in classes:
            # Quan trọng: userData phải là class_subject_id để histogram dùng được
            self.classFilterComboBox.addItem(cls['class_name'], userData=cls['class_subject_id'])