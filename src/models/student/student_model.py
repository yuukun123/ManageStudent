import sqlite3
from datetime import datetime

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
                f.faculty_name,
                m.major_name,
                c.class_name,
                ay.start_year || ' - ' || ay.end_year AS academic_year,
                s.enrollment_year,
                semesters.semester_name,
                s.gpa,
                s.accumulated_credits,
                s.attendance_rate,
                s.scholarship_info
            FROM students s
            LEFT JOIN majors m ON s.major_id = m.major_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
            LEFT JOIN semesters ON s.semester = semesters.semester_id
            LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
        """)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        students = [dict(zip(columns, row)) for row in rows]  # ✅ CHUYỂN TUPLE -> DICT
        return students
    except Exception as e:
        print("❌ Error loading students:", e)
        return []
    finally:
        conn.close()


def get_students_by_class_ids(class_ids: list):
    """Lấy sinh viên chỉ từ những lớp được phép."""
    if not class_ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Tạo chuỗi placeholder (?,?,?) động
    placeholders = ', '.join('?' for _ in class_ids)
    query = f"""
        SELECT
            s.student_id, s.full_name, s.gender, s.date_of_birth, s.email, s.phone_number, s.address, f.faculty_id,
            f.faculty_name, m.major_name, c.class_id, c.class_name,
            (ay.start_year || '-' || ay.end_year) as academic_year,
            s.enrollment_year, sem.semester_name, s.gpa, s.accumulated_credits,
            s.attendance_rate, s.scholarship_info
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
        LEFT JOIN majors m ON s.major_id = m.major_id
        LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
        LEFT JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
        LEFT JOIN semesters sem ON s.semester = sem.semester_id
        WHERE s.class_id IN ({placeholders})
    """
    cursor.execute(query, class_ids)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

# def get_student_score(class_ids: list):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     placeholders = ', '.join('?' for _ in class_ids)
#     query = f"""
#     SELECT
#         s.student_id,
#         s.full_name,
#         f.faculty_name,
#         m.major_name,
#         c.class_name,
#         sc.midterm_score,
#         sc.final_score,
#         sc.process_score
#     FROM scores sc
#     JOIN students s ON sc.student_id = s.student_id
#     JOIN classes c ON s.class_id = c.class_id
#     JOIN majors m ON s.major_id = m.major_id
#     JOIN faculties f ON m.faculty_id = f.faculty_id
#     WHERE c.class_id IN ({placeholders})
#     """
#     cursor.execute(query, class_ids)
#     rows = cursor.fetchall()
#     conn.close()
#
#     # Chuyển kết quả thành list[dict]
#     return [
#         {
#             "student_id": row[0],
#             "full_name": row[1],
#             "faculty_name": row[2],
#             "major_name": row[3],
#             "class_name": row[4],
#             "midterm_score": row[5],
#             "final_score": row[6],
#             "process_score": row[7],
#         }
#         for row in rows
#     ]


def get_student_scores_for_subject(class_ids: list, teacher_id: int, subject_id: int):
    """
    Lấy danh sách sinh viên và điểm của họ cho một môn học cụ thể
    dựa trên các lớp và giáo viên được chỉ định.
    Hàm này không quan tâm đến "năm học hiện tại", nó sẽ lấy tất cả các điểm
    khớp với phân công của giáo viên.
    """
    if not class_ids or not teacher_id or not subject_id:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ', '.join('?' for _ in class_ids)

    # Câu truy vấn được thiết kế lại để đi từ phân công giảng dạy (teacher_assignments)
    # và tìm sinh viên tương ứng. Đây là cách tiếp cận logic nhất.
    query = f"""
        SELECT
            s.student_id,
            s.full_name,
            f.faculty_id,
            f.faculty_name,
            m.major_name,
            c.class_id,
            c.class_name,
            sc.midterm_score,
            sc.final_score,
            sc.process_score,
            ay.start_year || '-' || ay.end_year as academic_year  -- Thêm thông tin năm học cho dễ hiển thị
        FROM 
            teacher_assignments ta

        -- Tìm tất cả sinh viên thuộc lớp được phân công
        JOIN students s ON ta.class_id = s.class_id

        -- Lấy thông tin chi tiết của sinh viên
        JOIN classes c ON s.class_id = c.class_id
        JOIN majors m ON s.major_id = m.major_id
        JOIN faculties f ON m.faculty_id = f.faculty_id
        JOIN academic_years ay ON ta.academic_year_id = ay.academic_year_id

        -- Tìm class_subject_id để liên kết với bảng điểm
        JOIN class_subjects cs ON ta.class_id = cs.class_id 
                               AND ta.subject_id = cs.subject_id 
                               AND ta.semester_id = cs.semester_id

        -- LEFT JOIN với bảng điểm
        LEFT JOIN scores sc ON s.student_id = sc.student_id 
                           AND cs.class_subject_id = sc.class_subject_id
                           -- Ràng buộc điểm phải thuộc đúng năm học của phân công
                           AND sc.year = ay.start_year
        WHERE
            ta.teacher_id = ?
            AND ta.subject_id = ?
            AND ta.class_id IN ({placeholders})

        -- GROUP BY để đảm bảo mỗi sinh viên chỉ có một hàng cho mỗi năm học
        -- (xử lý trường hợp một giáo viên được phân công dạy cùng 1 lớp, 1 môn trong nhiều năm)
        GROUP BY s.student_id, ta.academic_year_id
        ORDER BY s.full_name, ay.start_year;
    """

    # Thứ tự params giờ rất đơn giản
    params = (teacher_id, subject_id, *class_ids)

    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows

# Sửa hàm này trước
def get_subjects_by_teacher_and_classes(teacher_id, class_ids: list):
    """
    Lấy danh sách các môn học (ID và tên) mà một giáo viên dạy
    cho một danh sách các lớp.
    """
    if not class_ids:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dùng Row Factory cho dễ
    cursor = conn.cursor()

    placeholders = ', '.join('?' for _ in class_ids)
    query = f"""
        SELECT DISTINCT s.subject_id, s.subject_name
        FROM teacher_assignments ta
        JOIN subjects s ON ta.subject_id = s.subject_id
        WHERE ta.teacher_id = ? AND ta.class_id IN ({placeholders})
    """

    params = (teacher_id,) + tuple(class_ids)
    cursor.execute(query, params)

    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subjects

# def get_subject_by_teacher_and_class(teacher_id, class_ids):
#     import sqlite3
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#
#     # Đảm bảo class_ids là list, nếu chỉ là 1 giá trị thì chuyển thành list
#     if isinstance(class_ids, int):
#         class_ids = [class_ids]
#
#     placeholders = ', '.join('?' for _ in class_ids)
#     query = f"""
#         SELECT s.subject_name
#         FROM teacher_assignments t
#         JOIN subjects s ON t.subject_id = s.subject_id
#         WHERE t.teacher_id = ? AND t.class_id IN ({placeholders})
#     """
#
#     params = (teacher_id,) + tuple(class_ids)
#     cursor.execute(query, params)
#
#     row = cursor.fetchone()
#     conn.close()
#     return row[0] if row else "Unknown subject"


def add_score(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (
            student_id, full_name, gender, date_of_birth, email,
            phone_number, address, faculty_id, major_id, class_id, academic_year_id,
            enrollment_year, semester, gpa, accumulated_credits,
            attendance_rate, scholarship_info
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["student_id"],
        data["full_name"],
        data["gender"],
        data["date_of_birth"],
        data["email"],
        data["phone_number"],
        data["address"],
        data["faculty_id"],
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

def update_score(student_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET
            full_name = ?, gender = ?, date_of_birth = ?, email = ?,
            phone_number = ?, address = ?, faculty_id = ?, major_id = ?, class_id = ?,
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
        data["faculty_id"],
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

