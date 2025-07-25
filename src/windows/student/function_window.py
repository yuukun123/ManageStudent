from src.constants.form_mode import FormMode
from src.views.student.student_form_view import StudentForm

def open_add_edit_student_score(parent, mode: FormMode, default_faculty_id = None, default_class_id= None, student_data=None, subject_id=None, class_subject_id=None, year=None):
    dialog = StudentForm(
        parent=parent,
        mode=mode,
        default_faculty_id=default_faculty_id,
        default_class_id=default_class_id,
        student_data=student_data,
        subject_id=subject_id,
        class_subject_id=class_subject_id,
        year=year
    )
    if dialog.exec_():
        return dialog.get_form_data()
    return None

