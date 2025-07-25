from PyQt5.QtWidgets import QComboBox
from src.models.student.faculty_model import get_all_faculties
from src.models.student.class_model import get_classes_by_faculty_id


def setup_faculty_filter(filter_combo: QComboBox, teacher_context=None, block_signals=True):
    """
    Điền dữ liệu vào ComboBox Khoa.
    :param filter_combo: Widget QComboBox để điền.
    :param teacher_context: Context của giáo viên.
    :param block_signals: True nếu muốn chặn tín hiệu trong quá trình điền.
    """
    if block_signals:
        filter_combo.blockSignals(True)

    filter_combo.clear()
    filter_combo.addItem("All faculty", -1)

    faculties = teacher_context.get("faculties", []) if teacher_context else []
    for fid, fname in faculties:
        filter_combo.addItem(fname, fid)

    if block_signals:
        filter_combo.blockSignals(False)

def setup_classroom_filter(filter_combo: QComboBox, faculty_id: int, teacher_context=None, block_signals=True):
    """
    Điền dữ liệu vào ComboBox Lớp, KHÔNG có tùy chọn "All".
    """
    if block_signals:
        filter_combo.blockSignals(True)

    filter_combo.clear()
    # << BỎ DÒNG NÀY: filter_combo.addItem("All classroom", -1) >>

    classes_to_show = []
    allowed_classes = teacher_context.get("classes", []) if teacher_context else []

    if faculty_id == -1:
        # Nếu chọn "All faculty", hiển thị tất cả các lớp của giáo viên
        classes_to_show = [(cid, cname) for cid, cname, fid in allowed_classes]
    else:
        # Nếu chọn một khoa cụ thể, chỉ hiển thị các lớp trong khoa đó
        classes_to_show = [(cid, cname) for cid, cname, fid in allowed_classes if fid == faculty_id]

    sorted_classes = sorted(classes_to_show, key=lambda x: x[1])

    if not sorted_classes:
        filter_combo.addItem("No classes found", -1)  # Thêm item thông báo nếu không có lớp
    else:
        for cid, cname in sorted_classes:
            filter_combo.addItem(cname, cid)

    if block_signals:
        filter_combo.blockSignals(False)
