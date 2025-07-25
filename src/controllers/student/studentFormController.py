from src.utils.validators import is_valid_email, is_valid_phone
from src.models.student.student_model import add_score, get_subject_weights, update_score


# from src.models.student.major_model import get_all_majors
# from src.models.student.academic_year_model import get_all_academic_years

class StudentFormController:
    def __init__(self, view, subject_id = None):
        self.view = view
        # self.setup_major_comboboxes()
        # self.setup_academic_year_comboboxes()
        self.subject_id = subject_id
        self.weights = self._load_weights()

    def _load_weights(self):
        if not self.subject_id:
            return

        return get_subject_weights(self.subject_id)

    def calculate_process_score(self):
        """
        Lấy điểm giữa kỳ và cuối kỳ, tính điểm quá trình và cập nhật lên UI.
        """
        if not self.weights:
            self.view.inputProcessScore.setText("N/A")
            return

        try:
            # Lấy văn bản từ QLineEdit
            midterm_text = self.view.inputMidtermScore.text().strip()
            final_text = self.view.inputFinalScore.text().strip()

            # Chuyển đổi sang số, nếu rỗng hoặc không hợp lệ thì coi như là 0
            midterm_score = float(midterm_text) if midterm_text else 0.0
            final_score = float(final_text) if final_text else 0.0

            # Lấy trọng số từ thuộc tính self.weights
            midterm_weight = self.weights.get('midterm_weight', 0.0) # Trọng số giữa kỳ
            final_weight = self.weights.get('final_weight', 0.0) # Trọng số cuối kỳ

            # --- ĐÂY LÀ CÔNG THỨC TÍNH ĐIỂM CỦA BẠN ---
            # Ví dụ: Điểm quá trình = 30% giữa kỳ + 70% cuối kỳ
            # BẠN CÓ THỂ THAY ĐỔI CÔNG THỨC NÀY
            process_score = (midterm_weight * midterm_score) + (final_weight * final_score)

            # Làm tròn đến 1 chữ số thập phân
            process_score_str = f"{process_score:.1f}"

            # Cập nhật giá trị lên QLineEdit của điểm quá trình
            # Nên setReadOnly(True) cho ô này để người dùng không tự sửa
            self.view.inputProcessScore.setText(process_score_str)

        except ValueError:
            # Nếu người dùng nhập chữ thay vì số, không làm gì cả hoặc hiển thị lỗi
            self.view.inputProcessScore.setText("Invalid")
        except Exception as e:
            print(f"Error calculating process score: {e}")

    # def handle_add(self):
    #     data = self.view.get_form_data()
    #
    #     # if not is_valid_email(data["email"]):
    #     #     self.view.show_error("Email không hợp lệ.")
    #     #     return
    #     #
    #     # if not is_valid_phone(data["phone_number"]):
    #     #     self.view.show_error("Số điện thoại không hợp lệ.")
    #     #     return
    #
    #     # Nếu ok thì gọi model để lưu
    #     add_score(data)
    #     self.view.close()

    def handle_save(self):
        self.view.accept()

    def handle_update(self):
        data = self.view.get_form_data()
        update_score(data)
        self.view.close()

    # def setup_major_comboboxes(self):
    #     majors = get_all_majors()
    #     self.view.inputMajor.clear()
    #     self.view.inputMajor.addItem("Choose major")
    #     for major_id, major_name in majors:
    #         self.view.inputMajor.addItem(major_name, major_id)
    #
    # def setup_academic_year_comboboxes(self):
    #     academic_years = get_all_academic_years()
    #     self.view.inputAcademicYear.clear()
    #     self.view.inputAcademicYear.addItem("Choose academic year")
    #     for academic_year_id, start_year, end_year in academic_years:
    #         self.view.inputAcademicYear.addItem(academic_year_id, f"{start_year} - {end_year}")


