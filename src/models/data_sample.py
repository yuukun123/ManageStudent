import sqlite3
import random
from datetime import datetime
from faker import Faker
from werkzeug.security import generate_password_hash

fake = Faker()


def hash_password(password):
    return generate_password_hash(password)


def seed_data():
    conn = sqlite3.connect("../data/student_management.db")
    cursor = conn.cursor()

    try:
        print("🧹 Clearing old data...")
        tables = [
            'audit_logs', 'scores', 'class_students', 'teacher_assignments',
            'enrollments', 'class_subjects', 'students', 'subjects', 'users',
            'classes', 'majors', 'academic_years', 'semesters', 'faculties'
        ]
        for table in tables:
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(f"DELETE FROM {table};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table}';")
        print("✅ Old data cleared.")

        # === BẮT ĐẦU THÊM DỮ LIỆU MỚI ===

        # 1. FACULTIES
        print("🌱 Seeding Faculties...")
        faculties_data = [
            ('Information Technology',), ('Business Administration',), ('Arts and Humanities',), ('Engineering',)
        ]
        cursor.executemany("INSERT INTO faculties (faculty_name) VALUES (?)", faculties_data)
        FACULTY_COUNT = len(faculties_data)

        # 2. SEMESTERS
        print("🌱 Seeding Semesters...")
        semesters_data = [
            (1, 'Fall Semester'), (2, 'Spring Semester'), (3, 'Summer Semester'),
        ]
        cursor.executemany("INSERT INTO semesters (semester_id, semester_name) VALUES (?, ?)", semesters_data)
        SEMESTER_COUNT = len(semesters_data)

        # 3. ACADEMIC YEARS
        print("🌱 Seeding Academic Years...")
        academic_years_data = [
            (2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025),
            (2025, 2026),  # <-- ID 5, năm học mục tiêu của chúng ta
            (2026, 2027),  # ID 6
            (2027, 2028),  # ID 7
        ]
        cursor.executemany("INSERT INTO academic_years (start_year, end_year) VALUES (?, ?)", academic_years_data)
        ACADEMIC_YEAR_COUNT = len(academic_years_data)
        TARGET_ACADEMIC_YEAR_ID = 5  # ID của năm học 2025-2026

        # 4. MAJORS
        print("🌱 Seeding Majors...")
        majors_data = [
            ('Software Engineering', 1), ('Computer Science', 1), ('Data Science', 1), ('Cybersecurity', 1), ('Information Systems', 1),
            ('Business Management', 2), ('Marketing', 2), ('Finance', 2), ('Accounting', 2), ('International Business', 2),
            ('English Literature', 3), ('History', 3), ('Philosophy', 3), ('Fine Arts', 3), ('Music Theory', 3),
            ('Mechanical Engineering', 4), ('Civil Engineering', 4), ('Electrical Engineering', 4), ('Chemical Engineering', 4), ('Aerospace Engineering', 4)
        ]
        cursor.executemany("INSERT INTO majors (major_name, faculty_id) VALUES (?, ?)", majors_data)
        MAJOR_COUNT = len(majors_data)

        # 5. CLASSES
        print("🌱 Seeding Classes...")
        classes_data = []
        class_prefixes = ['IT', 'BA', 'AH', 'EN']
        for i in range(FACULTY_COUNT):
            faculty_id = i + 1
            for j in range(4):  # Chỉ tạo đến năm 2024 để lớp 2025 là duy nhất
                class_name = f"{class_prefixes[i]}-{2021 + j}"
                classes_data.append((class_name, faculty_id))

        # Thêm lớp học cụ thể cho kịch bản test
        classes_data.append(('CS2025', 1))  # Lớp cho năm học 2025, khoa CNTT
        cursor.executemany("INSERT INTO classes (class_name, faculty_id) VALUES (?, ?)", classes_data)
        CLASS_COUNT = len(classes_data)
        TARGET_CLASS_ID = CLASS_COUNT  # ID của lớp CS2025 sẽ là ID cuối cùng

        # 6. SUBJECTS
        print("🌱 Seeding Subjects...")
        subjects_data = [
            ('Advanced Algorithms', 4, 0.4, 0.6),  # Môn học mục tiêu, ID=1
        ]
        for _ in range(24):
            mid_weight = round(random.choice([0.3, 0.4, 0.5]), 2)
            final_weight = round(1.0 - mid_weight, 2)
            subjects_data.append(
                (fake.catch_phrase().title(), random.randint(2, 4), mid_weight, final_weight)
            )
        cursor.executemany("INSERT INTO subjects (subject_name, credit, midterm_weight, final_weight) VALUES (?, ?, ?, ?)", subjects_data)
        SUBJECT_COUNT = len(subjects_data)
        TARGET_SUBJECT_ID = 1  # ID của môn Advanced Algorithms

        # 7. USERS (Admin & Teachers)
        print("🌱 Seeding Users (Admin & Teachers)...")
        users_data = [
            ('admin', hash_password('admin123'), 'admin', 'System Administrator', 'N/A', '1980-01-01', 'admin@university.edu', '0900000000', '1 Admin Road', None, None, None),
            # Giáo viên cụ thể cho kịch bản test, thuộc khoa CNTT (faculty_id = 1)
            ('test.teacher', hash_password('teacher123'), 'teacher', 'Dr. Test Teacher', 'Male', '1988-08-08', 'test.teacher@university.edu', '0123456789', '123 Test St', 'PhD in AI', 1, 1)
        ]
        # Thêm các giáo viên ngẫu nhiên khác
        for i in range(19):
            full_name = fake.name()
            name_parts = full_name.split()
            first_name = name_parts[0].lower()
            last_name = name_parts[-1].lower()
            short_username = f"t.{first_name}{last_name[0]}{i}"
            email = f"{short_username}@university.edu"
            faculty_id = random.randint(1, FACULTY_COUNT)
            users_data.append(
                (
                    short_username, hash_password('teacher123'), 'teacher', full_name,
                    random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=28, maximum_age=65).strftime('%Y-%m-%d'),
                    email, fake.phone_number(), fake.address(), f"PhD in {fake.bs()}", faculty_id, 1
                )
            )
        cursor.executemany("INSERT INTO users (username, password_hash, role, full_name, gender, date_of_birth, email, phone_number, address, major, faculty_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", users_data)
        TARGET_TEACHER_ID = 2  # ID của test.teacher

        # 8. STUDENTS
        print("🌱 Seeding Students...")
        students_data = []
        # Tạo 5 sinh viên cụ thể cho kịch bản test
        print("🌱 Seeding specific students for class CS2025...")
        target_students_ids = []
        for i in range(5):
            student_id = f"25CS{str(i + 1).zfill(3)}"
            target_students_ids.append(student_id)
            students_data.append((
                student_id, fake.name(), random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=19).strftime('%Y-%m-%d'),
                f"student.cs25.{i + 1}@university.edu", fake.phone_number(), fake.address(),
                1,  # Major ID (Software Engineering)
                TARGET_CLASS_ID,  # Class ID (CS2025)
                TARGET_ACADEMIC_YEAR_ID,  # Academic Year ID
                2025,  # Enrollment Year
                1,  # Semester
                None, None, None, None  # Điểm GPA, tín chỉ, v.v. sẽ được tính sau
            ))

        # Tạo các sinh viên ngẫu nhiên khác
        for i in range(95):
            enrollment_year = random.randint(2021, 2024)
            class_id = random.randint(1, CLASS_COUNT - 1)  # Tránh lớp CS2025
            cursor.execute("SELECT faculty_id FROM classes WHERE class_id = ?", (class_id,))
            faculty_id = cursor.fetchone()[0]
            cursor.execute("SELECT major_id FROM majors WHERE faculty_id = ?", (faculty_id,))
            possible_majors = [row[0] for row in cursor.fetchall()]
            major_id = random.choice(possible_majors)
            full_name = fake.name()
            first_name = full_name.split()[0].lower()
            student_id = f"{str(enrollment_year)[-2:]}{class_prefixes[faculty_id - 1]}{str(i + 1).zfill(3)}"
            students_data.append((
                student_id, full_name, random.choice(['Male', 'Female']), fake.date_of_birth(minimum_age=18, maximum_age=23).strftime('%Y-%m-%d'),
                f"{first_name}{i + 1}@student.university.edu", fake.phone_number(), fake.address(),
                major_id, class_id, random.randint(1, ACADEMIC_YEAR_COUNT - 1), enrollment_year,
                random.randint(1, SEMESTER_COUNT), round(random.uniform(1.5, 4.0), 2),
                random.randint(10, 120), round(random.uniform(0.75, 1.0), 2),
                random.choice([None, 'Merit Scholarship', 'Dean\'s List'])
            ))
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", students_data)

        # 9. CLASS_STUDENTS
        print("🌱 Seeding Class-Student relationships...")
        class_students_data = [(s[8], s[0]) for s in students_data]
        cursor.executemany("INSERT INTO class_students (class_id, student_id) VALUES (?, ?)", class_students_data)

        # 10. CLASS_SUBJECTS
        print("🌱 Seeding Class-Subject (Curriculum)...")
        class_subjects_data = []
        for class_id in range(1, CLASS_COUNT + 1):
            subjects_for_class = random.sample(range(1, SUBJECT_COUNT + 1), k=8)
            for subject_id in subjects_for_class:
                semester_id = random.randint(1, 2)
                class_subjects_data.append((class_id, subject_id, semester_id))
        # Đảm bảo lớp mục tiêu có môn học mục tiêu
        class_subjects_data.append((TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1))
        unique_class_subjects = list(set(class_subjects_data))
        cursor.executemany("INSERT INTO class_subjects (class_id, subject_id, semester_id) VALUES (?, ?, ?)", unique_class_subjects)

        # 11. ENROLLMENTS
        print("🌱 Seeding Enrollments...")
        enrollments_data = []
        for student_tuple in students_data:
            student_id, class_id = student_tuple[0], student_tuple[8]
            cursor.execute("SELECT subject_id, semester_id FROM class_subjects WHERE class_id = ?", (class_id,))
            subjects_for_class = cursor.fetchall()
            for subject_id, semester_id in subjects_for_class:
                enrollments_data.append((student_id, subject_id, semester_id))
        cursor.executemany("INSERT INTO enrollments (student_id, subject_id, semester_id) VALUES (?, ?, ?)", enrollments_data)

        # 12. TEACHER ASSIGNMENTS
        print("🌱 Seeding Teacher Assignments...")
        teacher_assignments_data = []
        # Thêm phân công cụ thể cho kịch bản test
        teacher_assignments_data.append((TARGET_TEACHER_ID, TARGET_CLASS_ID, TARGET_SUBJECT_ID, 1, TARGET_ACADEMIC_YEAR_ID))
        # Thêm các phân công ngẫu nhiên khác
        # ... (Bạn có thể giữ lại hoặc xóa phần tạo phân công ngẫu nhiên ở đây nếu muốn) ...
        unique_assignments = list(set(teacher_assignments_data))
        cursor.executemany("INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, semester_id, academic_year_id) VALUES (?, ?, ?, ?, ?)", unique_assignments)

        # 13. SCORES
        print("🌱 Seeding Scores...")
        scores_data = []
        # Thêm điểm cụ thể cho kịch bản test
        print(f"🌱 Seeding specific scores for class {TARGET_CLASS_ID} and subject {TARGET_SUBJECT_ID}...")
        cursor.execute("SELECT class_subject_id FROM class_subjects WHERE class_id = ? AND subject_id = ?", (TARGET_CLASS_ID, TARGET_SUBJECT_ID))
        target_cs_id = cursor.fetchone()[0]

        for student_id in target_students_ids:
            scores_data.append((
                student_id,
                target_cs_id,
                2025,  # Năm học
                round(random.uniform(6.0, 9.5), 1),
                round(random.uniform(5.0, 9.8), 1),
                round(random.uniform(7.0, 10.0), 1)
            ))

        # Thêm các điểm ngẫu nhiên khác
        # ... (Bạn có thể giữ lại hoặc xóa phần tạo điểm ngẫu nhiên ở đây nếu muốn) ...
        unique_scores = list(set(scores_data))
        cursor.executemany(
            "INSERT INTO scores (student_id, class_subject_id, year, midterm_score, final_score, process_score) VALUES (?, ?, ?, ?, ?, ?)",
            unique_scores
        )

        # --- HOÀN TẤT ---
        conn.commit()
        print("\n✅ All data seeded successfully!")
        print("----------------- SPECIFIC TEST SCENARIO -----------------")
        print(f"  - Teacher Username: test.teacher")
        print(f"  - Teacher Password: teacher123")
        print(f"  - Assigned to teach subject '{'Advanced Algorithms'}' (ID: {TARGET_SUBJECT_ID})")
        print(f"  - For class '{'CS2025'}' (ID: {TARGET_CLASS_ID})")
        print(f"  - In academic year '{'2025-2026'}' (ID: {TARGET_ACADEMIC_YEAR_ID})")
        print(f"  - 5 specific students with scores have been added to this class.")
        print("----------------------------------------------------------")

    except sqlite3.Error as e:
        print(f"\n❌ An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_data()