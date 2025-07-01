from src.constants.form_mode import FormMode
from src.views.student.student_form_view import StudentForm

def open_add_edit_student(parent, mode: FormMode, student_data=None):
    dialog = StudentForm(parent=parent, mode=mode, student_data=student_data)
    if dialog.exec_():
        return dialog.get_data()
    return None

