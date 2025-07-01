import sqlite3

def create_db():
    conn = sqlite3.connect("../data/student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """),

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
        FOREIGN KEY (academic_year_id) REFERENCES academic_years(academic_year_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        address TEXT NOT NULL,
        major TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS majors (
        major_id INTEGER PRIMARY KEY AUTOINCREMENT,
        major_name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_years (
        academic_year_id INT AUTO_INCREMENT PRIMARY KEY,
        start_year INT,
        end_year INT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INT AUTO_INCREMENT PRIMARY KEY,
        subject_name VARCHAR(100),
        credit INT,
        midterm_weight FLOAT NOT NULL, 
        final_weight FLOAT NOT NULL     
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        subject_id INT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_subjects (
        class_subject_id INT AUTO_INCREMENT PRIMARY KEY,
        class_id INT,
        subject_id INT,
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_teachers (
        class_teacher_id INT AUTO_INCREMENT PRIMARY KEY,
        class_id INT,
        teacher_id INT,
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS class_students (
        class_student_id INT AUTO_INCREMENT PRIMARY KEY,
        class_id INT,
        student_id INT,
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """)


    cursor.execute("""
    CREATE TABLE scores (
        score_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        subject_id INT,
        semester INT,
        year INT,
        midterm_score FLOAT,
        final_score FLOAT,
        process_score FLOAT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE if not exists audit_logs (
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semesters (
        semester_id INTEGER PRIMARY KEY,
        semester_name TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM semesters")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO semesters (semester_id, semester_name) VALUES (?, ?)
        """, [
            (1, "semester 1"),
            (2, "semester 2"),
            (3, "summer semester")
        ])


    conn.commit()
    conn.close()
    print("✅ Database & table created successfully!")

if __name__ == "__main__":
    create_db()
