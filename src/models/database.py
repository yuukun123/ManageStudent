import sqlite3

def create_db():
    conn = sqlite3.connect("../data/student_management.db")
    cursor = conn.cursor()

    # USERS (GỘP TEACHERS + ADMIN + ROLE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL, -- 'admin' hoặc 'teacher'
        full_name TEXT,
        gender TEXT,
        date_of_birth TEXT,
        email TEXT,
        phone_number TEXT,
        address TEXT,
        major TEXT,
        faculty_id INTEGER,
        created_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id)
    )
    """)


    # FACULTIES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculties (
        faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_name TEXT NOT NULL
    )
    """)

    # SEMESTERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semesters (
        semester_id INTEGER PRIMARY KEY,
        semester_name TEXT NOT NULL
    )
    """)

    # MAJORS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS majors (
        major_id INTEGER PRIMARY KEY AUTOINCREMENT,
        major_name TEXT NOT NULL,
        faculty_id INTEGER,
        FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id)
    )
    """)

    # CLASSES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        faculty_id INTEGER,
        FOREIGN KEY (faculty_id) REFERENCES faculties(faculty_id)
    )
    """)

    # ACADEMIC YEARS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_years (
        academic_year_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_year INT,
        end_year INT
    )
    """)

    # STUDENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id VARCHAR(20) PRIMARY KEY,
        full_name VARCHAR(100),
        gender VARCHAR(10),
        date_of_birth DATE,
        email VARCHAR(100),
        phone_number VARCHAR(20),
        address TEXT,
        major_id INT,
        class_id INT,
        academic_year_id INT,
        enrollment_year INT,
        semester INT,
        gpa FLOAT,
        accumulated_credits INT,
        attendance_rate FLOAT,
        scholarship_info TEXT,
        FOREIGN KEY (major_id) REFERENCES majors(major_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (academic_year_id) REFERENCES academic_years(academic_year_id),
        FOREIGN KEY (semester) REFERENCES semesters(semester_id)
    )
    """)

    # SUBJECTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name VARCHAR(100),
        credit INT,
        midterm_weight FLOAT NOT NULL,
        final_weight FLOAT NOT NULL
    )
    """)

    # ENROLLMENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id VARCHAR(20),
        subject_id INT,
        semester_id INT,
        UNIQUE(student_id, subject_id, semester_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (semester_id) REFERENCES semesters(semester_id)
    )
    """)

    # CLASS SUBJECTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_subjects (
        class_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INT,
        subject_id INT,
        semester_id INT,
        UNIQUE(class_id, subject_id, semester_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (semester_id) REFERENCES semesters(semester_id)
    )
    """)

    # TEACHER ASSIGNMENTS (tham chiếu trực tiếp tới users.id nếu role='teacher')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INT,  -- users.id với role='teacher'
        class_id INT,
        subject_id INT,
        semester_id INT,
        academic_year_id INT,
        UNIQUE(teacher_id, class_id, subject_id, semester_id, academic_year_id),
        FOREIGN KEY (teacher_id) REFERENCES users(id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (semester_id) REFERENCES semesters(semester_id),
        FOREIGN KEY (academic_year_id) REFERENCES academic_years(academic_year_id)
    )
    """)

    # CLASS STUDENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_students (
        class_student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INT,
        student_id VARCHAR(20),
        UNIQUE(class_id, student_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)

    # SCORES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        score_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id VARCHAR(20),
        class_subject_id INT, -- Liên kết rõ lớp-môn-học kỳ
        year INT,
        midterm_score FLOAT,
        final_score FLOAT,
        process_score FLOAT,
        UNIQUE(student_id, class_subject_id, year),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (class_subject_id) REFERENCES class_subjects(class_subject_id)
    )
    """)

    # AUDIT LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        table_name TEXT,
        record_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database & table created successfully!")

if __name__ == "__main__":
    create_db()
