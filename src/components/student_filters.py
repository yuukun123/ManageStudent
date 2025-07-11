from PyQt5.QtWidgets import QComboBox
from src.models.student.faculty_model import get_all_faculties
from src.models.student.class_model import get_classes_by_faculty_id

def setup_faculty_filter(filterFacultyStudent: QComboBox, teacher_context=None):
    filterFacultyStudent.blockSignals(True)
    filterFacultyStudent.clear()
    filterFacultyStudent.addItem("All faculty", -1)

    faculties = teacher_context.get("faculties", []) if teacher_context else []
    for fid, fname in faculties:
        filterFacultyStudent.addItem(fname, fid)

    filterFacultyStudent.blockSignals(False)

def setup_classroom_filter(filterClassroomStudent: QComboBox, faculty_id: int, teacher_context=None):
    filterClassroomStudent.blockSignals(True)
    filterClassroomStudent.clear()
    filterClassroomStudent.addItem("All classroom", -1)

    classes_to_show = []
    allowed_classes = teacher_context.get("classes", []) if teacher_context else []

    if faculty_id == -1:
        classes_to_show = [(cid, cname) for cid, cname, fid in allowed_classes]
    else:
        classes_to_show = [(cid, cname) for cid, cname, fid in allowed_classes if fid == faculty_id]

    for cid, cname in sorted(classes_to_show, key=lambda x: x[1]):
        filterClassroomStudent.addItem(cname, cid)

    filterClassroomStudent.blockSignals(False)
