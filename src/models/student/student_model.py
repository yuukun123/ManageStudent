import sqlite3

DB_PATH = "data/student_management.db"

def get_all_students():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.student_id,
                s.full_name,
                s.gender,
                s.date_of_birth,
                s.email,
                s.phone_number,
                s.address,
                m.major_name,
                c.class_name,
                ay.start_year || ' - ' || ay.end_year AS academic_year,
                s.enrollment_year,
                s.semester,
                s.gpa,
                s.accumulated_credits,
                s.attendance_rate,
                s.scholarship_info
            FROM students s
            LEFT JOIN majors m ON s.major_id = m.major_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
        """)
        students = cursor.fetchall()
        return students
    except Exception as e:
        print("❌ Error loading students:", e)
        return []
    finally:
        conn.close()



def get_student_by_id(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def add_student(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            student_id, full_name, gender, date_of_birth, email,
            phone_number, address, major_id, class_id, academic_year_id,
            enrollment_year, semester, gpa, accumulated_credits,
            attendance_rate, scholarship_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["student_id"],
        data["full_name"],
        data["gender"],
        data["date_of_birth"],
        data["email"],
        data["phone_number"],
        data["address"],
        data["major_id"],
        data["class_id"],
        data["academic_year_id"],
        data["enrollment_year"],
        data["semester"],
        data["gpa"],
        data["accumulated_credits"],
        data["attendance_rate"],
        data["scholarship_info"]
    ))
    conn.commit()
    conn.close()

def update_student(student_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET
            full_name = ?, gender = ?, date_of_birth = ?, email = ?,
            phone_number = ?, address = ?, major_id = ?, class_id = ?,
            academic_year_id = ?, enrollment_year = ?, semester = ?,
            gpa = ?, accumulated_credits = ?, attendance_rate = ?, scholarship_info = ?
        WHERE student_id = ?
    """, (
        data["full_name"],
        data["gender"],
        data["date_of_birth"],
        data["email"],
        data["phone_number"],
        data["address"],
        data["major_id"],
        data["class_id"],
        data["academic_year_id"],
        data["enrollment_year"],
        data["semester"],
        data["gpa"],
        data["accumulated_credits"],
        data["attendance_rate"],
        data["scholarship_info"],
        student_id
    ))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

# if __name__ == "__main__":
#     # Ví dụ thêm user
#     if __name__ == "__main__":
#         sample_student = {
#             "student_id": "123456",
#             "full_name": "Nguyen Van A",
#             "gender": "Nam",
#             "date_of_birth": "1990-01-01",
#             "email": "Q5kYv@example.com",
#             "phone_number": "1234567890",
#             "address": "123 Main St, Anytown, USA",
#             "major_id": 1,
#             "class_id": 1,
#             "academic_year_id": 1,
#             "enrollment_year": 2021,
#             "semester": 1,
#             "gpa": 3.5,
#             "accumulated_credits": 120,
#             "attendance_rate": 0.9,
#             "scholarship_info": "None"
#         }
#
#         add_student(sample_student)
