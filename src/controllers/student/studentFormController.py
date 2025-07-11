from src.utils.validators import is_valid_email, is_valid_phone
# from src.models.student.student_model import add_student
from src.models.student.major_model import get_all_majors
from src.models.student.academic_year_model import get_all_academic_years

class StudentFormController:
    def __init__(self, view):
        self.view = view
        self.setup_major_comboboxes()
        # self.setup_academic_year_comboboxes()

    def handle_save(self):
        data = self.view.get_form_data()

        if not is_valid_email(data["email"]):
            self.view.show_error("Email không hợp lệ.")
            return

        if not is_valid_phone(data["phone_number"]):
            self.view.show_error("Số điện thoại không hợp lệ.")
            return

        # Nếu ok thì gọi model để lưu
        add_student(data)
        self.view.close()

    def setup_major_comboboxes(self):
        majors = get_all_majors()
        self.view.inputMajor.clear()
        self.view.inputMajor.addItem("Choose major")
        for major_id, major_name in majors:
            self.view.inputMajor.addItem(major_name, major_id)

    def setup_academic_year_comboboxes(self):
        academic_years = get_all_academic_years()
        self.view.inputAcademicYear.clear()
        self.view.inputAcademicYear.addItem("Choose academic year")
        for academic_year_id, start_year, end_year in academic_years:
            self.view.inputAcademicYear.addItem(academic_year_id, f"{start_year} - {end_year}")


