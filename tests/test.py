# trong file: tests/test.py

import os
import sys
from pprint import pprint

# --- SỬA LẠI ĐOẠN CODE NÀY ---
# Giả sử file này nằm trong tests/
# Đường dẫn gốc của dự án là thư mục cha của tests/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
# --- KẾT THÚC SỬA LỖI ---

# Bây giờ import sẽ hoạt động
from src.models.student.student_model import (
    get_all_students,
    get_students_by_class_ids,
    get_student_by_id,
    get_current_academic_year_id,
    get_student_scores_for_subject,
    get_subjects_by_teacher_and_classes
)

def run_tests():
    """Chạy tất cả các bài test cho các hàm truy vấn."""

    print("\n" + "=" * 20 + " BÀI TEST 1: get_all_students " + "=" * 20)
    all_students = get_all_students()
    print(f"-> Tìm thấy tổng cộng {len(all_students)} sinh viên.")
    if all_students:
        print("-> Dữ liệu của 2 sinh viên đầu tiên:")
        pprint(all_students[:2])

    # ... (phần còn lại của file test không cần thay đổi) ...
    print("\n" + "=" * 20 + " BÀI TEST 2: get_students_by_class_ids " + "=" * 20)
    class_ids_to_test = [2, 17]
    print(f"-> Đang tìm sinh viên cho các lớp có ID: {class_ids_to_test}")
    students_by_class = get_students_by_class_ids(class_ids_to_test)
    print(f"-> Tìm thấy {len(students_by_class)} sinh viên.")
    if students_by_class:
        print("-> Dữ liệu của một vài sinh viên tìm được:")
        pprint(students_by_class[:3])

    print("\n" + "=" * 20 + " BÀI TEST 3: get_student_by_id " + "=" * 20)
    if all_students:
        student_id_to_test = all_students[0]['student_id']
        print(f"-> Đang tìm sinh viên có ID: {student_id_to_test}")
        single_student = get_student_by_id(student_id_to_test)
        print("-> Kết quả:")
        pprint(single_student)
    else:
        print("-> Bỏ qua vì không có sinh viên nào để lấy ID.")

    print("\n" + "=" * 20 + " BÀI TEST 4: get_current_academic_year_id " + "=" * 20)
    current_year_id = get_current_academic_year_id()
    print(f"-> ID năm học hiện tại được xác định là: {current_year_id}")

    print("\n" + "=" * 20 + " BÀI TEST 5: get_subjects_by_teacher_and_classes " + "=" * 20)
    teacher_id_test = 2
    class_ids_test = [17]
    print(f"-> Đang tìm môn học cho giáo viên ID={teacher_id_test} ở lớp ID={class_ids_test}")
    subjects = get_subjects_by_teacher_and_classes(teacher_id_test, class_ids_test)
    print("-> Kết quả:")
    pprint(subjects)

    print("\n" + "=" * 20 + " BÀI TEST 6: get_student_scores_for_subject (Kịch bản thành công) " + "=" * 20)
    if subjects and current_year_id:
        subject_id_test = subjects[0]['subject_id']
        print(f"-> Đang tìm điểm của lớp ID={class_ids_test} cho môn ID={subject_id_test}, giáo viên ID={teacher_id_test} trong năm học ID={current_year_id}")
        scores = get_student_scores_for_subject(
            class_ids=class_ids_test,
            teacher_id=teacher_id_test,
            subject_id=subject_id_test,
            academic_year_id=current_year_id
        )
        print(f"-> Tìm thấy {len(scores)} bản ghi điểm.")
        if scores:
            print("-> Dữ liệu điểm của một vài sinh viên:")
            pprint(scores[:3])
    else:
        print("-> Bỏ qua vì không đủ dữ liệu từ các bài test trước (môn học hoặc năm học).")

if __name__ == "__main__":
    run_tests()