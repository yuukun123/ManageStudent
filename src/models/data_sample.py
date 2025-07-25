import sqlite3
import random
from faker import Faker
from werkzeug.security import generate_password_hash

fake = Faker()


def hash_password(password):
    """Băm mật khẩu bằng phương thức an toàn."""
    return generate_password_hash(password)


def seed_data():
    """Kết nối CSDL, xóa dữ liệu cũ và tạo dữ liệu mới một cách đầy đủ và an toàn."""
    conn = sqlite3.connect("../data/student_management.db")
    cursor = conn.cursor()

    try:
        print("🧹 Clearing old data...")
        tables = [
            'audit_logs', 'scores', 'class_students', 'teacher_assignments',
            'enrollments', 'class_subjects', 'students', 'subjects', 'users',
            'classes', 'majors', 'academic_years', 'semesters', 'faculties'
        ]
        cursor.execute("PRAGMA foreign_keys = OFF;")
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table}';")
        cursor.execute("PRAGMA foreign_keys = ON;")
        print("✅ Old data cleared.")

        # === BẮT ĐẦU THÊM DỮ LIỆU MỚI ===

        # 1. Dữ liệu cơ bản
        print("🌱 Seeding basic data...")
        faculties_data = [('Information Technology',), ('Business Administration',), ('Arts and Humanities',), ('Engineering',)]
        cursor.executemany("INSERT INTO faculties (faculty_name) VALUES (?)", faculties_data)
        FACULTY_COUNT = len(faculties_data)
        semesters_data = [(1, 'Fall Semester'), (2, 'Spring Semester'), (3, 'Summer Semester')]
        cursor.executemany("INSERT INTO semesters (semester_id, semester_name) VALUES (?, ?)", semesters_data)
        academic_years_data = [(2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025), (2025, 2026), (2026, 2027), (2027, 2028)]
        cursor.executemany("INSERT INTO academic_years (start_year, end_year) VALUES (?, ?)", academic_years_data)
        ACADEMIC_YEAR_COUNT = len(academic_years_data)
        TARGET_ACADEMIC_YEAR_ID = 5
        majors_data = [
            ('Software Engineering', 1), ('Computer Science', 1), ('Data Science', 1), ('Cybersecurity', 1), ('Information Systems', 1),
            ('Business Management', 2), ('Marketing', 2), ('Finance', 2), ('Accounting', 2), ('International Business', 2),
            ('English Literature', 3), ('History', 3), ('Philosophy', 3), ('Fine Arts', 3), ('Music Theory', 3),
            ('Mechanical Engineering', 4), ('Civil Engineering', 4), ('Electrical Engineering', 4), ('Chemical Engineering', 4), ('Aerospace Engineering', 4)
        ]
        cursor.executemany("INSERT INTO majors (major_name, faculty_id) VALUES (?, ?)", majors_data)

        # 2. LỚP HỌC (CLASSES)
        print("🌱 Seeding Classes...")
        classes_data = []
        class_prefixes = ['IT', 'BA', 'AH', 'EN']
        for i in range(FACULTY_COUNT):
            for j in range(4):
                classes_data.append((f"{class_prefixes[i]}-{2021 + j}", i + 1))

        classes_data.append(('CS2025', 1))
        cursor.executemany("INSERT INTO classes (class_name, faculty_id) VALUES (?, ?)", classes_data)

        cursor.execute("SELECT class_id FROM classes WHERE class_name = 'CS2025'")
        TARGET_CLASS_ID = cursor.fetchone()[0]

        # <<< SỬA LỖI Ở ĐÂY: Tạo danh sách các lớp KHÔNG BAO GỒM lớp test >>>
        cursor.execute("SELECT class_id FROM classes WHERE class_id != ?", (TARGET_CLASS_ID,))
        RANDOM_CLASS_IDS = [row[0] for row in cursor.fetchall()]

        # 3. MÔN HỌC (SUBJECTS)
        print("🌱 Seeding Subjects...")
        cursor.execute("INSERT INTO subjects (subject_name, credit, midterm_weight, final_weight) VALUES (?, ?, ?, ?)",
                       ('Advanced Algorithms', 4, 0.4, 0.6))
        TARGET_SUBJECT_ID = cursor.lastrowid
        subjects_data = []
        for _ in range(24):
            mid_weight = round(random.choice([0.3, 0.4, 0.5]), 2)
            subjects_data.append((fake.catch_phrase().title(), random.randint(2, 4), mid_weight, round(1.0 - mid_weight, 2)))
        cursor.executemany("INSERT INTO subjects (subject_name, credit, midterm_weight, final_weight) VALUES (?, ?, ?, ?)", subjects_data)
        SUBJECT_COUNT = TARGET_SUBJECT_ID + len(subjects_data)

        # 4. NGƯỜI DÙNG (USERS)
        print("🌱 Seeding Users with full details...")
        users_data = [
            ('admin', hash_password('admin123'), 'admin', 'System Administrator', 'N/A', '1980-01-01', 'admin@university.edu', '0900000000', '1 Admin Road', None, None, None),
            ('test.teacher', hash_password('teacher123'), 'teacher', 'Dr. Test Teacher', 'Male', '1988-08-08', 'test.teacher@university.edu', '0123456789', '123 Test St', 'PhD in AI', 1, 1)
        ]
        for i in range(19):
            full_name = fake.name()
            username = f"t.{full_name.split()[0].lower()}{full_name.split()[-1][0].lower()}{i}"
            users_data.append((
                username, hash_password('teacher123'), 'teacher', full_name,
                random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=28, maximum_age=65).strftime('%Y-%m-%d'),
                f"{username}@university.edu", fake.phone_number(), fake.address(), f"PhD in {fake.bs()}", random.randint(1, FACULTY_COUNT), 1
            ))
        cursor.executemany("INSERT INTO users (username, password_hash, role, full_name, gender, date_of_birth, email, phone_number, address, major, faculty_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", users_data)
        cursor.execute("SELECT id FROM users WHERE username = 'test.teacher'")
        TARGET_TEACHER_ID = cursor.fetchone()[0]

        # 5. SINH VIÊN (STUDENTS)
        print("🌱 Seeding Students with logical class assignments...")
        students_data = []
        target_students_ids = []

        # Tạo 5 sinh viên cụ thể cho kịch bản test
        for i in range(5):
            student_id = f"25CS{str(i + 1).zfill(3)}"
            target_students_ids.append(student_id)
            students_data.append((
                student_id, fake.name(), random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=19).strftime('%Y-%m-%d'),
                f"student.cs25.{i + 1}@university.edu", fake.phone_number(), fake.address(),
                1, TARGET_CLASS_ID, TARGET_ACADEMIC_YEAR_ID, 2025, 1,
                None, None, None, None
            ))

        # Tạo 95 sinh viên ngẫu nhiên khác
        for i in range(95):
            enrollment_year = random.randint(2021, 2024)
            # <<< SỬA LỖI Ở ĐÂY: Chỉ chọn lớp từ danh sách các lớp ngẫu nhiên >>>
            class_id = random.choice(RANDOM_CLASS_IDS)

            cursor.execute("SELECT faculty_id FROM classes WHERE class_id = ?", (class_id,))
            faculty_id = cursor.fetchone()[0]
            cursor.execute("SELECT major_id FROM majors WHERE faculty_id = ?", (faculty_id,))
            possible_majors = [row[0] for row in cursor.fetchall()]
            major_id = random.choice(possible_majors) if possible_majors else 1
            full_name = fake.name()
            student_id = f"{str(enrollment_year)[-2:]}{class_prefixes[faculty_id - 1]}{str(i + 1).zfill(3)}"
            students_data.append((
                student_id, full_name, random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=23).strftime('%Y-%m-%d'),
                f"{full_name.split()[0].lower()}{i + 1}@student.university.edu", fake.phone_number(), fake.address(),
                major_id, class_id, random.randint(1, 4), enrollment_year, random.randint(1, 2),
                round(random.uniform(1.5, 4.0), 2), random.randint(10, 120), round(random.uniform(0.75, 1.0), 2),
                random.choice([None, 'Merit Scholarship', 'Dean\'s List'])
            ))
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students_data)

        # Các phần còn lại không có lỗi, giữ nguyên logic tạo điểm an toàn
        # 6. Bảng quan hệ
        print("🌱 Seeding relationship tables...")
        cursor.execute("SELECT class_id, student_id FROM students")
        cursor.executemany("INSERT INTO class_students (class_id, student_id) VALUES (?, ?)", cursor.fetchall())

        cursor.execute("SELECT class_id FROM classes")
        all_class_ids_for_curriculum = [row[0] for row in cursor.fetchall()]
        class_subjects_data = []
        for class_id in all_class_ids_for_curriculum:
            subjects_for_class = random.sample(range(1, SUBJECT_COUNT + 1), k=min(8, SUBJECT_COUNT))
            for subject_id in subjects_for_class:
                class_subjects_data.append((class_id, subject_id, random.randint(1, 2)))
        class_subjects_data.append((TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1))
        cursor.executemany("INSERT OR IGNORE INTO class_subjects (class_id, subject_id, semester_id) VALUES (?, ?, ?)", list(set(class_subjects_data)))

        cursor.execute("SELECT cs.student_id, csub.subject_id, csub.semester_id FROM class_students cs JOIN class_subjects csub ON cs.class_id = csub.class_id")
        cursor.executemany("INSERT OR IGNORE INTO enrollments (student_id, subject_id, semester_id) VALUES (?, ?, ?)", list(set(cursor.fetchall())))

        # 7. PHÂN CÔNG GIÁO VIÊN
        print("🌱 Seeding Teacher Assignments...")
        cursor.execute("SELECT id FROM users WHERE role='teacher'")
        all_teacher_ids = [row[0] for row in cursor.fetchall()]
        teacher_assignments_data = []
        teacher_assignments_data.append((TARGET_TEACHER_ID, TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1, TARGET_ACADEMIC_YEAR_ID))
        cursor.execute("SELECT class_subject_id, class_id, subject_id, semester_id FROM class_subjects")
        all_class_subjects = cursor.fetchall()
        for cs_id, class_id, subject_id, semester_id in random.sample(all_class_subjects, k=min(len(all_class_subjects), 60)):
            cursor.execute("SELECT faculty_id FROM classes WHERE class_id = ?", (class_id,))
            faculty_id_res = cursor.fetchone()
            if faculty_id_res:
                faculty_id = faculty_id_res[0]
                cursor.execute("SELECT id FROM users WHERE role='teacher' AND faculty_id = ?", (faculty_id,))
                possible_teachers = [row[0] for row in cursor.fetchall()]
                if possible_teachers:
                    teacher_id = random.choice(possible_teachers)
                    academic_year_id = random.randint(1, ACADEMIC_YEAR_COUNT)
                    teacher_assignments_data.append((teacher_id, class_id, subject_id, semester_id, academic_year_id))
        unique_assignments = list(set(teacher_assignments_data))
        cursor.executemany("INSERT OR IGNORE INTO teacher_assignments (teacher_id, class_id, subject_id, semester_id, academic_year_id) VALUES (?, ?, ?, ?, ?)", unique_assignments)

        # 8. ĐIỂM SỐ
        print("🌱 Seeding Scores safely...")
        scores_dict = {}
        # Điểm cho kịch bản test
        cursor.execute("SELECT class_subject_id FROM class_subjects WHERE class_id = ? AND subject_id = ?", (TARGET_CLASS_ID, TARGET_SUBJECT_ID))
        target_cs_id_res = cursor.fetchone()
        if target_cs_id_res:
            target_cs_id = target_cs_id_res[0]
            for student_id in target_students_ids:
                unique_key = (student_id, target_cs_id, 2025)
                scores_dict[unique_key] = (student_id, target_cs_id, 2025, round(random.uniform(6.0, 9.5), 1), round(random.uniform(5.0, 9.8), 1), round(random.uniform(7.0, 10.0), 1))
        # Điểm ngẫu nhiên
        for teacher_id, class_id, subject_id, semester_id, academic_year_id in random.sample(unique_assignments, k=min(len(unique_assignments), 40)):
            cursor.execute("SELECT class_subject_id FROM class_subjects WHERE class_id = ? AND subject_id = ? AND semester_id = ?", (class_id, subject_id, semester_id))
            cs_id_res = cursor.fetchone()
            if not cs_id_res: continue
            cs_id = cs_id_res[0]
            cursor.execute("SELECT start_year FROM academic_years WHERE academic_year_id = ?", (academic_year_id,))
            year_res = cursor.fetchone()
            if not year_res: continue
            year = year_res[0]
            cursor.execute("SELECT student_id FROM class_students WHERE class_id = ?", (class_id,))
            students_in_class = [row[0] for row in cursor.fetchall()]
            for student_id in students_in_class:
                if random.random() < 0.8:
                    unique_key = (student_id, cs_id, year)
                    scores_dict[unique_key] = (student_id, cs_id, year, round(random.uniform(3.0, 10.0), 1), round(random.uniform(3.0, 10.0), 1), round(random.uniform(5.0, 10.0), 1))
        unique_scores = list(scores_dict.values())
        cursor.executemany("INSERT INTO scores (student_id, class_subject_id, year, midterm_score, final_score, process_score) VALUES (?, ?, ?, ?, ?, ?)", unique_scores)

        # --- HOÀN TẤT ---
        conn.commit()
        print("\n✅ All data seeded successfully!")
        print("----------------- SPECIFIC TEST SCENARIO -----------------")
        print(f"  - Teacher Username: test.teacher (ID: {TARGET_TEACHER_ID})")
        print(f"  - Teacher Password: teacher123")
        print(f"  - Assigned to teach subject: 'Advanced Algorithms' (ID: {TARGET_SUBJECT_ID})")
        print(f"  - For class: 'CS2025' (ID: {TARGET_CLASS_ID})")
        print(f"  - In academic year: '2025-2026' (ID: {TARGET_ACADEMIC_YEAR_ID})")
        print(f"  - 5 specific students have been added to this class.")
        print("----------------------------------------------------------")

    except sqlite3.Error as e:
        print(f"\n❌ An error occurred: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    seed_data()

# import sqlite3
# import random
# from datetime import datetime
# from faker import Faker
# from werkzeug.security import generate_password_hash
#
# fake = Faker()
#
#
# def hash_password(password):
#     return generate_password_hash(password)
#
#
# def seed_data():
#     conn = sqlite3.connect("../data/student_management.db")
#     cursor = conn.cursor()
#
#     try:
#         print("🧹 Clearing old data...")
#         tables = [
#             'audit_logs', 'scores', 'class_students', 'teacher_assignments',
#             'enrollments', 'class_subjects', 'students', 'subjects', 'users',
#             'classes', 'majors', 'academic_years', 'semesters', 'faculties'
#         ]
#         for table in tables:
#             cursor.execute("PRAGMA foreign_keys = ON;")
#             cursor.execute(f"DELETE FROM {table};")
#             cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table}';")
#         print("✅ Old data cleared.")
#
#         # === BẮT ĐẦU THÊM DỮ LIỆU MỚI ===
#
#         # 1. FACULTIES
#         print("🌱 Seeding Faculties...")
#         faculties_data = [
#             ('Information Technology',), ('Business Administration',), ('Arts and Humanities',), ('Engineering',)
#         ]
#         cursor.executemany("INSERT INTO faculties (faculty_name) VALUES (?)", faculties_data)
#         FACULTY_COUNT = len(faculties_data)
#
#         # 2. SEMESTERS
#         print("🌱 Seeding Semesters...")
#         semesters_data = [
#             (1, 'Fall Semester'), (2, 'Spring Semester'), (3, 'Summer Semester'),
#         ]
#         cursor.executemany("INSERT INTO semesters (semester_id, semester_name) VALUES (?, ?)", semesters_data)
#         SEMESTER_COUNT = len(semesters_data)
#
#         # 3. ACADEMIC YEARS
#         print("🌱 Seeding Academic Years...")
#         academic_years_data = [
#             (2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025),
#             (2025, 2026),  # <-- ID 5, năm học mục tiêu của chúng ta
#             (2026, 2027),  # ID 6
#             (2027, 2028),  # ID 7
#         ]
#         cursor.executemany("INSERT INTO academic_years (start_year, end_year) VALUES (?, ?)", academic_years_data)
#         ACADEMIC_YEAR_COUNT = len(academic_years_data)
#         TARGET_ACADEMIC_YEAR_ID = 5  # ID của năm học 2025-2026
#
#         # 4. MAJORS
#         print("🌱 Seeding Majors...")
#         majors_data = [
#             ('Software Engineering', 1), ('Computer Science', 1), ('Data Science', 1), ('Cybersecurity', 1), ('Information Systems', 1),
#             ('Business Management', 2), ('Marketing', 2), ('Finance', 2), ('Accounting', 2), ('International Business', 2),
#             ('English Literature', 3), ('History', 3), ('Philosophy', 3), ('Fine Arts', 3), ('Music Theory', 3),
#             ('Mechanical Engineering', 4), ('Civil Engineering', 4), ('Electrical Engineering', 4), ('Chemical Engineering', 4), ('Aerospace Engineering', 4)
#         ]
#         cursor.executemany("INSERT INTO majors (major_name, faculty_id) VALUES (?, ?)", majors_data)
#         MAJOR_COUNT = len(majors_data)
#
#         # 5. CLASSES
#         print("🌱 Seeding Classes...")
#         classes_data = []
#         class_prefixes = ['IT', 'BA', 'AH', 'EN']
#         for i in range(FACULTY_COUNT):
#             faculty_id = i + 1
#             for j in range(4):  # Chỉ tạo đến năm 2024 để lớp 2025 là duy nhất
#                 class_name = f"{class_prefixes[i]}-{2021 + j}"
#                 classes_data.append((class_name, faculty_id))
#
#         # Thêm lớp học cụ thể cho kịch bản test
#         classes_data.append(('CS2025', 1))  # Lớp cho năm học 2025, khoa CNTT
#         cursor.executemany("INSERT INTO classes (class_name, faculty_id) VALUES (?, ?)", classes_data)
#         CLASS_COUNT = len(classes_data)
#         TARGET_CLASS_ID = CLASS_COUNT  # ID của lớp CS2025 sẽ là ID cuối cùng
#
#         # 6. SUBJECTS
#         print("🌱 Seeding Subjects...")
#         subjects_data = [
#             ('Advanced Algorithms', 4, 0.4, 0.6),  # Môn học mục tiêu, ID=1
#         ]
#         for _ in range(24):
#             mid_weight = round(random.choice([0.3, 0.4, 0.5]), 2)
#             final_weight = round(1.0 - mid_weight, 2)
#             subjects_data.append(
#                 (fake.catch_phrase().title(), random.randint(2, 4), mid_weight, final_weight)
#             )
#         cursor.executemany("INSERT INTO subjects (subject_name, credit, midterm_weight, final_weight) VALUES (?, ?, ?, ?)", subjects_data)
#         SUBJECT_COUNT = len(subjects_data)
#         TARGET_SUBJECT_ID = 1  # ID của môn Advanced Algorithms
#
#         # 7. USERS (Admin & Teachers)
#         print("🌱 Seeding Users (Admin & Teachers)...")
#         users_data = [
#             ('admin', hash_password('admin123'), 'admin', 'System Administrator', 'N/A', '1980-01-01', 'admin@university.edu', '0900000000', '1 Admin Road', None, None, None),
#             # Giáo viên cụ thể cho kịch bản test, thuộc khoa CNTT (faculty_id = 1)
#             ('test.teacher', hash_password('teacher123'), 'teacher', 'Dr. Test Teacher', 'Male', '1988-08-08', 'test.teacher@university.edu', '0123456789', '123 Test St', 'PhD in AI', 1, 1)
#         ]
#         # Thêm các giáo viên ngẫu nhiên khác
#         for i in range(19):
#             full_name = fake.name()
#             name_parts = full_name.split()
#             first_name = name_parts[0].lower()
#             last_name = name_parts[-1].lower()
#             short_username = f"t.{first_name}{last_name[0]}{i}"
#             email = f"{short_username}@university.edu"
#             faculty_id = random.randint(1, FACULTY_COUNT)
#             users_data.append(
#                 (
#                     short_username, hash_password('teacher123'), 'teacher', full_name,
#                     random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=28, maximum_age=65).strftime('%Y-%m-%d'),
#                     email, fake.phone_number(), fake.address(), f"PhD in {fake.bs()}", faculty_id, 1
#                 )
#             )
#         cursor.executemany("INSERT INTO users (username, password_hash, role, full_name, gender, date_of_birth, email, phone_number, address, major, faculty_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", users_data)
#         TARGET_TEACHER_ID = 2  # ID của test.teacher
#
#         # 8. STUDENTS
#         print("🌱 Seeding Students...")
#         students_data = []
#         # Tạo 5 sinh viên cụ thể cho kịch bản test
#         print("🌱 Seeding specific students for class CS2025...")
#         target_students_ids = []
#         for i in range(5):
#             student_id = f"25CS{str(i + 1).zfill(3)}"
#             target_students_ids.append(student_id)
#             students_data.append((
#                 student_id, fake.name(), random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=19).strftime('%Y-%m-%d'),
#                 f"student.cs25.{i + 1}@university.edu", fake.phone_number(), fake.address(),
#                 1,  # Major ID (Software Engineering)
#                 TARGET_CLASS_ID,  # Class ID (CS2025)
#                 TARGET_ACADEMIC_YEAR_ID,  # Academic Year ID
#                 2025,  # Enrollment Year
#                 1,  # Semester
#                 None, None, None, None  # Điểm GPA, tín chỉ, v.v. sẽ được tính sau
#             ))
#
#         # Tạo các sinh viên ngẫu nhiên khác
#         for i in range(95):
#             enrollment_year = random.randint(2021, 2024)
#             class_id = random.randint(1, CLASS_COUNT - 1)  # Tránh lớp CS2025
#             cursor.execute("SELECT faculty_id FROM classes WHERE class_id = ?", (class_id,))
#             faculty_id = cursor.fetchone()[0]
#             cursor.execute("SELECT major_id FROM majors WHERE faculty_id = ?", (faculty_id,))
#             possible_majors = [row[0] for row in cursor.fetchall()]
#             major_id = random.choice(possible_majors)
#             full_name = fake.name()
#             first_name = full_name.split()[0].lower()
#             student_id = f"{str(enrollment_year)[-2:]}{class_prefixes[faculty_id - 1]}{str(i + 1).zfill(3)}"
#             students_data.append((
#                 student_id, full_name, random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=23).strftime('%Y-%m-%d'),
#                 f"{first_name}{i + 1}@student.university.edu", fake.phone_number(), fake.address(),
#                 major_id, class_id, random.randint(1, ACADEMIC_YEAR_COUNT - 1), enrollment_year,
#                 random.randint(1, SEMESTER_COUNT), round(random.uniform(1.5, 4.0), 2),
#                 random.randint(10, 120), round(random.uniform(0.75, 1.0), 2),
#                 random.choice([None, 'Merit Scholarship', 'Dean\'s List'])
#             ))
#         cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students_data)
#
#         # 9. CLASS_STUDENTS
#         print("🌱 Seeding Class-Student relationships...")
#         class_students_data = [(s[8], s[0]) for s in students_data]
#         cursor.executemany("INSERT INTO class_students (class_id, student_id) VALUES (?, ?)", class_students_data)
#
#         # 10. CLASS_SUBJECTS
#         print("🌱 Seeding Class-Subject (Curriculum)...")
#         class_subjects_data = []
#         for class_id in range(1, CLASS_COUNT + 1):
#             subjects_for_class = random.sample(range(1, SUBJECT_COUNT + 1), k=8)
#             for subject_id in subjects_for_class:
#                 semester_id = random.randint(1, 2)
#                 class_subjects_data.append((class_id, subject_id, semester_id))
#         # Đảm bảo lớp mục tiêu có môn học mục tiêu
#         class_subjects_data.append((TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1))
#         unique_class_subjects = list(set(class_subjects_data))
#         cursor.executemany("INSERT INTO class_subjects (class_id, subject_id, semester_id) VALUES (?, ?, ?)", unique_class_subjects)
#
#         # 11. ENROLLMENTS
#         print("🌱 Seeding Enrollments...")
#         enrollments_data = []
#         for student_tuple in students_data:
#             student_id, class_id = student_tuple[0], student_tuple[8]
#             cursor.execute("SELECT subject_id, semester_id FROM class_subjects WHERE class_id = ?", (class_id,))
#             subjects_for_class = cursor.fetchall()
#             for subject_id, semester_id in subjects_for_class:
#                 enrollments_data.append((student_id, subject_id, semester_id))
#         cursor.executemany("INSERT INTO enrollments (student_id, subject_id, semester_id) VALUES (?, ?, ?)", enrollments_data)
#
#         # 12. TEACHER ASSIGNMENTS
#         print("🌱 Seeding Teacher Assignments...")
#         teacher_assignments_data = []
#         # Thêm phân công cụ thể cho kịch bản test
#         teacher_assignments_data.append((TARGET_TEACHER_ID, TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1, TARGET_ACADEMIC_YEAR_ID))
#         # Thêm các phân công ngẫu nhiên khác
#         # --- Tạo các phân công ngẫu nhiên cho các năm học CŨ (ID 1-4) ---
#         cursor.execute("SELECT class_subject_id, class_id FROM class_subjects")
#         all_class_subjects = cursor.fetchall()
#         for cs_id, class_id in all_class_subjects:
#             cursor.execute("SELECT faculty_id FROM classes WHERE class_id = ?", (class_id,))
#             faculty_id = cursor.fetchone()[0]
#             cursor.execute("SELECT id FROM users WHERE role='teacher' AND faculty_id = ?", (faculty_id,))
#             possible_teachers = [row[0] for row in cursor.fetchall()]
#             if possible_teachers:
#                 teacher_id = random.choice(possible_teachers)
#                 cursor.execute("SELECT subject_id, semester_id FROM class_subjects WHERE class_subject_id = ?", (cs_id,))
#                 subject_id, semester_id = cursor.fetchone()
#                 assignment = (teacher_id, class_id, subject_id, semester_id, random.randint(1, 4))
#                 teacher_assignments_data.append(assignment)
#
#         # --- Tạo các phân công mới một cách có hệ thống hơn cho các năm học MỚI (ID 5, 6, 7) ---
#         print("🌱 Seeding more robust assignments for future academic years (5, 6, 7)...")
#         new_academic_year_ids = [5, 6, 7]
#         specific_assignments_for_scores = []  # Lưu lại để tạo điểm
#
#         # Lấy tất cả giáo viên (ID từ 2 đến 21)
#         all_teacher_ids = list(range(2, 22))
#
#         # Vòng lặp qua TỪNG NĂM HỌC MỚI để đảm bảo mỗi năm đều có phân công
#         for year_id in new_academic_year_ids:
#             print(f"   -> Generating assignments for Academic Year ID: {year_id}")
#             # Với mỗi năm học, chọn ngẫu nhiên 5-10 giáo viên để phân công
#             teachers_for_this_year = random.sample(all_teacher_ids, k=random.randint(5, 10))
#
#             for teacher_id in teachers_for_this_year:
#                 # Tìm một lớp/môn ngẫu nhiên cho giáo viên này
#                 cursor.execute("""
#                     SELECT c.class_id, cs.subject_id, cs.semester_id
#                     FROM classes c
#                     JOIN class_subjects cs ON c.class_id = cs.class_id
#                     WHERE c.faculty_id = (SELECT faculty_id FROM users WHERE id = ?)
#                     ORDER BY RANDOM() LIMIT 1
#                 """, (teacher_id,))
#
#                 details = cursor.fetchone()
#                 if details:
#                     class_id, subject_id, semester_id = details
#                     # Tạo phân công cho năm học hiện tại của vòng lặp
#                     new_assignment = (teacher_id, class_id, subject_id, semester_id, year_id)
#
#                     teacher_assignments_data.append(new_assignment)
#                     specific_assignments_for_scores.append(new_assignment)
#                     print(f"      - Assigning teacher {teacher_id} to class {class_id} for subject {subject_id}")
#         unique_assignments = list(set(teacher_assignments_data))
#         cursor.executemany("INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, semester_id, academic_year_id) VALUES (?, ?, ?, ?, ?)", unique_assignments)
#
#         # 13. SCORES
#         print("🌱 Seeding Scores...")
#         scores_data = []
#         # Thêm điểm cụ thể cho kịch bản test
#         print(f"🌱 Seeding specific scores for class {TARGET_CLASS_ID} and subject {TARGET_SUBJECT_ID}...")
#         cursor.execute("SELECT class_subject_id FROM class_subjects WHERE class_id = ? AND subject_id = ?", (TARGET_CLASS_ID, TARGET_SUBJECT_ID))
#         target_cs_id = cursor.fetchone()[0]
#
#         for student_id in target_students_ids:
#             scores_data.append((
#                 student_id,
#                 target_cs_id,
#                 2025,  # Năm học
#                 round(random.uniform(6.0, 9.5), 1),
#                 round(random.uniform(5.0, 9.8), 1),
#                 round(random.uniform(7.0, 10.0), 1)
#             ))
#
#         # Thêm các điểm ngẫu nhiên khác
#         # ... (Bạn có thể giữ lại hoặc xóa phần tạo điểm ngẫu nhiên ở đây nếu muốn) ...
#         unique_scores = list(set(scores_data))
#         cursor.executemany(
#             "INSERT INTO scores (student_id, class_subject_id, year, midterm_score, final_score, process_score) VALUES (?, ?, ?, ?, ?, ?)",
#             unique_scores
#         )
#
#         # --- HOÀN TẤT ---
#         conn.commit()
#         print("\n✅ All data seeded successfully!")
#         print("----------------- SPECIFIC TEST SCENARIO -----------------")
#         print(f"  - Teacher Username: test.teacher")
#         print(f"  - Teacher Password: teacher123")
#         print(f"  - Assigned to teach subject '{'Advanced Algorithms'}' (ID: {TARGET_SUBJECT_ID})")
#         print(f"  - For class '{'CS2025'}' (ID: {TARGET_CLASS_ID})")
#         print(f"  - In academic year '{'2025-2026'}' (ID: {TARGET_ACADEMIC_YEAR_ID})")
#         print(f"  - 5 specific students with scores have been added to this class.")
#         print("----------------------------------------------------------")
#
#     except sqlite3.Error as e:
#         print(f"\n❌ An error occurred: {e}")
#         conn.rollback()
#     finally:
#         conn.close()
#
#
# if __name__ == "__main__":
#     seed_data()
#
