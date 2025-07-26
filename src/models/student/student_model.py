import os
import sqlite3
from datetime import datetime


# DB_PATH = "data/student_management.db"

# --- SỬA LẠI ĐOẠN CODE NÀY ---
# 1. Lấy đường dẫn của thư mục chứa file model này (src/models/student)
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Đi ngược lên 2 cấp để đến thư mục 'src'
#    Từ src/models/student/ -> đi lên -> src/models/ -> đi lên -> src/
SRC_ROOT = os.path.abspath(os.path.join(MODEL_DIR, '..', '..'))

# 3. Nối với thư mục 'data' và tên file CSDL
DB_PATH = os.path.join(SRC_ROOT, 'data', 'student_management.db')

# Dòng print này rất hữu ích để debug
print(f"[student_model.py] Corrected database path to: {DB_PATH}")
# --- KẾT THÚC SỬA LỖI ---

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
        if conn:
            conn.close()


# Thêm vào student_model.py

def get_assigned_students_for_teacher(teacher_id, academic_year_id, semester_id, class_id=None, faculty_id=None):
    """
    Lấy danh sách sinh viên thuộc các lớp mà giáo viên được phân công dạy
    trong một năm học và học kỳ cụ thể.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    params = [teacher_id, academic_year_id, semester_id]

    # Bắt đầu với các join cơ bản
    query = """
        SELECT DISTINCT
            s.student_id, s.full_name, s.gender, s.date_of_birth, s.email, s.phone_number,
            s.address, f.faculty_id, f.faculty_name, m.major_name, c.class_id, c.class_name,
            (ay_student.start_year || ' - ' || ay_student.end_year) AS academic_year,
            s.enrollment_year, sem.semester_name, s.gpa, s.accumulated_credits,
            s.attendance_rate, s.scholarship_info
        FROM 
            teacher_assignments ta
        JOIN 
            students s ON s.class_id = ta.class_id
        JOIN 
            semesters sem ON s.semester = sem.semester_id
        JOIN 
            classes c ON s.class_id = c.class_id
        JOIN
            faculties f ON c.faculty_id = f.faculty_id
        JOIN
            majors m ON s.major_id = m.major_id
        JOIN 
            academic_years ay_student ON s.academic_year_id = ay_student.academic_year_id -- Năm tuyển sinh của SV
        WHERE
            ta.teacher_id = ? 
            AND ta.academic_year_id = ?
            AND ta.semester_id = ?
    """

    # Thêm bộ lọc động (tùy chọn)
    if class_id and class_id != -1:
        query += " AND ta.class_id = ?"
        params.append(class_id)

    if faculty_id and faculty_id != -1:
        query += " AND c.faculty_id = ?"
        params.append(faculty_id)

    query += " ORDER BY s.full_name;"

    try:
        cursor.execute(query, tuple(params))
        students = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_assigned_students_for_teacher: {e}")
        students = []
    finally:
        conn.close()

    return students

# def get_students_by_criteria(
#         allowed_class_ids: list,
#         faculty_id: int = None,
#         class_id: int = None,
#         academic_year_id: int = None
# ):
#     """
#     Lấy danh sách sinh viên dựa trên nhiều tiêu chí lọc từ cơ sở dữ liệu.
#     Hàm này được tối ưu để chỉ truy vấn dữ liệu cần thiết.
#
#     Args:
#         allowed_class_ids (list): Danh sách ID các lớp mà người dùng được phép xem. Đây là tham số bắt buộc.
#         faculty_id (int, optional): ID của khoa để lọc. Mặc định là None.
#         class_id (int, optional): ID của lớp cụ thể để lọc. Mặc định là None.
#         academic_year_id (int, optional): ID của năm học để lọc. Mặc định là None.
#
#     Returns:
#         list: Một danh sách các dictionary, mỗi dictionary chứa thông tin một sinh viên.
#     """
#     # Điều kiện tiên quyết: phải có danh sách lớp được phép
#     if not allowed_class_ids:
#         return []
#
#     try:
#         conn = sqlite3.connect(DB_PATH)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#
#         # Bắt đầu xây dựng câu truy vấn và danh sách tham số
#         params = list(allowed_class_ids)
#
#         # Phần WHERE cơ bản, luôn luôn lọc theo các lớp được phép
#         where_clauses = [f"s.class_id IN ({','.join('?' for _ in allowed_class_ids)})"]
#
#         # Thêm các điều kiện lọc động nếu chúng được cung cấp
#         if faculty_id and faculty_id != -1:
#             where_clauses.append("c.faculty_id = ?")
#             params.append(faculty_id)
#
#         # Lưu ý: class_id cũng là một bộ lọc con trong các lớp được phép
#         if class_id and class_id != -1:
#             where_clauses.append("s.class_id = ?")
#             params.append(class_id)
#
#         if academic_year_id and academic_year_id != -1:
#             where_clauses.append("s.academic_year_id = ?")
#             params.append(academic_year_id)
#
#         # Ghép các mệnh đề WHERE lại với nhau
#         where_string = " AND ".join(where_clauses)
#
#         # Xây dựng câu truy vấn cuối cùng
#         query = f"""
#             SELECT
#                 s.student_id, s.full_name, s.gender, s.date_of_birth, s.email, s.phone_number,
#                 s.address, f.faculty_id, f.faculty_name, m.major_name, c.class_id, c.class_name,
#                 s.academic_year_id, -- Thêm cột này để có thể lọc
#                 (ay.start_year || ' - ' || ay.end_year) as academic_year,
#                 s.enrollment_year, sem.semester_name, s.gpa, s.accumulated_credits,
#                 s.attendance_rate, s.scholarship_info
#             FROM students s
#             LEFT JOIN classes c ON s.class_id = c.class_id
#             LEFT JOIN majors m ON s.major_id = m.major_id
#             LEFT JOIN faculties f ON c.faculty_id = f.faculty_id
#             LEFT JOIN academic_years ay ON s.academic_year_id = ay.academic_year_id
#             LEFT JOIN semesters sem ON s.semester = sem.semester_id
#             WHERE {where_string}
#         """
#
#         cursor.execute(query, tuple(params))
#         students = [dict(row) for row in cursor.fetchall()]
#
#     except sqlite3.Error as e:
#         print(f"Database error in get_students_by_criteria: {e}")
#         students = []
#     finally:
#         if 'conn' in locals() and conn:
#             conn.close()
#
#     return students

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

# def get_current_academic_year_id():
#     """
#     Tự động xác định ID của năm học hiện tại dựa trên ngày của hệ thống.
#     Một năm học (ví dụ: 2023-2024) được coi là "hiện tại" nếu ngày hiện tại
#     nằm trong khoảng từ tháng 8 năm bắt đầu đến tháng 7 năm kết thúc.
#     Ví dụ: Ngày 15/09/2023 -> thuộc năm học 2023-2024.
#            Ngày 15/06/2024 -> vẫn thuộc năm học 2023-2024.
#
#     Returns:
#         int: ID của năm học hiện tại, hoặc None nếu không tìm thấy.
#     """
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#
#     # Lấy ngày và năm hiện tại
#     now = datetime.now()
#     current_year = now.year
#
#     # Logic xác định năm bắt đầu của năm học hiện tại
#     # Nếu tháng hiện tại >= 8 (tháng 8), năm học bắt đầu từ năm nay.
#     # Ngược lại, năm học bắt đầu từ năm ngoái.
#     start_year_of_academic_session = current_year if now.month >= 8 else current_year - 1
#
#     query = """
#         SELECT academic_year_id
#         FROM academic_years
#         WHERE start_year = ?
#     """
#
#     try:
#         cursor.execute(query, (start_year_of_academic_session,))
#         result = cursor.fetchone()
#         academic_year_id = result[0] if result else None
#     except sqlite3.Error as e:
#         print(f"Database error in get_current_academic_year_id: {e}")
#         academic_year_id = None
#     finally:
#         conn.close()
#
#     print(f"Determined current academic year ID for start year {start_year_of_academic_session} -> ID: {academic_year_id}")
#     return academic_year_id


def get_all_academic_years():
    """
    Lấy danh sách các năm học từ quá khứ đến năm học hiện tại.
    Hàm này tự động cập nhật khi bước sang năm học mới.
    Dùng để điền vào bộ lọc ComboBox.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- BƯỚC 1: XÁC ĐỊNH NĂM BẮT ĐẦU CỦA NĂM HỌC HIỆN TẠI ---
    now = datetime.now()
    # Nếu tháng hiện tại >= 8 (tháng 8), năm học bắt đầu từ năm nay.
    # Ngược lại (tháng 1-7), năm học bắt đầu từ năm ngoái.
    current_academic_start_year = now.year if now.month >= 8 else now.year - 1

    # --- BƯỚC 2: SỬA ĐỔI CÂU TRUY VẤN SQL ---
    # Lấy tất cả các năm học có năm bắt đầu <= năm bắt đầu của năm học hiện tại
    query = """
        SELECT * 
        FROM academic_years 
        WHERE start_year <= ? 
        ORDER BY start_year DESC
    """

    try:
        cursor.execute(query, (current_academic_start_year,))
        years = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_all_academic_years: {e}")
        years = []
    finally:
        conn.close()

    return years

def get_student_scores_for_subject(
    class_ids: list,
    teacher_id: int,
    subject_id: int,
    academic_year_id: int  # <<< THÊM THAM SỐ NÀY
):
    """
    Lấy danh sách sinh viên và điểm của họ cho một môn học, một năm học cụ thể
    dựa trên các lớp và giáo viên được chỉ định.
    """
    if not isinstance(class_ids, list) or not class_ids or not teacher_id or not subject_id or not academic_year_id:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ', '.join('?' for _ in class_ids)

    # Câu truy vấn giờ đây sẽ có bộ lọc theo năm học
    query = f"""
        SELECT
            s.student_id,
            s.full_name,
            f.faculty_name,
            m.major_name,
            c.class_name,
            sc.midterm_score,
            sc.final_score,
            sc.process_score
        FROM 
            teacher_assignments ta
        JOIN 
            students s ON s.class_id = ta.class_id
                       --AND s.academic_year_id = ta.academic_year_id -- <<< THÊM DÒNG NÀY
        JOIN 
            class_subjects cs ON cs.class_id = ta.class_id 
                             AND cs.subject_id = ta.subject_id 
                             AND cs.semester_id = ta.semester_id
        LEFT JOIN 
            scores sc ON sc.student_id = s.student_id 
                      AND sc.class_subject_id = cs.class_subject_id
                      AND sc.year = (SELECT start_year FROM academic_years WHERE academic_year_id = ta.academic_year_id)
        JOIN 
            classes c ON s.class_id = c.class_id
        JOIN 
            majors m ON s.major_id = m.major_id
        JOIN 
            faculties f ON c.faculty_id = f.faculty_id
        WHERE
            ta.teacher_id = ?
            AND ta.subject_id = ?
            AND ta.academic_year_id = ?
            AND ta.class_id IN ({placeholders})
        ORDER BY
            s.full_name;
    """

    # Thêm academic_year_id vào danh sách tham số
    params = (teacher_id, subject_id, academic_year_id, *class_ids)

    try:
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        rows = []
    finally:
        conn.close()

    return rows

def get_all_classes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classes")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_all_subjects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_all_semesters():
    """Lấy tất cả các học kỳ từ bảng semesters."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Sắp xếp theo ID để đảm bảo thứ tự nhất quán (HK1, HK2, HK Hè)
        cursor.execute("SELECT * FROM semesters ORDER BY semester_id")

        semesters = [dict(row) for row in cursor.fetchall()]
        return semesters
    except sqlite3.Error as e:
        print(f"Database error in get_all_semesters: {e}")
        return []
    finally:
        if conn:
            conn.close()

# Sửa hàm này trước
def get_subjects_by_teacher_and_classes(teacher_id, class_ids, academic_year_id, semester_id):
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
        SELECT DISTINCT s.subject_id, s.subject_name, ta.semester_id
        FROM teacher_assignments ta
        JOIN subjects s ON ta.subject_id = s.subject_id
        WHERE ta.teacher_id = ? 
        AND ta.class_id IN ({placeholders})
        AND ta.academic_year_id = ?  -- Lọc theo năm học
        AND ta.semester_id = ?       -- Lọc theo học kỳ
    """

    params = (teacher_id, *class_ids, academic_year_id, semester_id)
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

# trong student_model.py (hoặc subject_model.py)

# Giả sử bảng subjects của bạn có các cột: midterm_weight, final_weight
def get_subject_weights(subject_id):
    """Lấy trọng số điểm giữa kỳ và cuối kỳ cho một môn học cụ thể."""
    if not subject_id:
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT midterm_weight, final_weight FROM subjects WHERE subject_id = ?"

    try:
        cursor.execute(query, (subject_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Database error in get_subject_weights: {e}")
        return None
    finally:
        conn.close()

# Trong student_model.py

def get_class_subject_id(class_id, subject_id, semester_id):
    """Lấy class_subject_id từ bảng class_subjects."""
    # Giả định bạn có semester_id, nếu không có thể cần logic khác
    if not all([class_id, subject_id, semester_id]):
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT class_subject_id FROM class_subjects WHERE class_id = ? AND subject_id = ? AND semester_id = ?"
    try:
        cursor.execute(query, (class_id, subject_id, semester_id))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_start_year_from_academic_id(academic_year_id):
    """Lấy start_year từ academic_year_id."""
    if not academic_year_id:
        return None
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT start_year FROM academic_years WHERE academic_year_id = ?"
    try:
        cursor.execute(query, (academic_year_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

# Sửa lại trong student_model.py
def add_score(data):
    """
    Thêm một bản ghi điểm mới vào bảng `scores`.

    Args:
        data (dict): Một dictionary chứa các thông tin cần thiết:
                     'student_id', 'class_subject_id', 'year',
                     'midterm_score', 'final_score', 'process_score'.
    """
    # Bạn cần lấy class_subject_id và year để có thể thêm điểm
    # Đây là những thông tin quan trọng cần được truyền vào form
    required_keys = ['student_id', 'class_subject_id', 'year', 'midterm_score', 'final_score', 'process_score']
    if not all(key in data for key in required_keys):
        print("Lỗi: Thiếu thông tin cần thiết để thêm điểm.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO scores (student_id, class_subject_id, year, midterm_score, final_score, process_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("student_id"),
            data.get("class_subject_id"),
            data.get("year"),
            data.get("midterm_score"),
            data.get("final_score"),
            data.get("process_score")
        ))
        conn.commit()
        print(f"✅ Đã thêm điểm thành công cho sinh viên ID: {data.get('student_id')}")
    except sqlite3.IntegrityError as e:
        # Lỗi này xảy ra nếu bạn cố thêm điểm cho sinh viên đã có điểm trong môn này
        # (Giả sử bạn có UNIQUE constraint trên student_id, class_subject_id, year)
        print(f"⚠️ Lỗi khi thêm điểm (có thể đã tồn tại): {e}. Cân nhắc dùng hàm update.")
    except sqlite3.Error as e:
        print(f"❌ Lỗi CSDL khi thêm điểm: {e}")
    finally:
        conn.close()


# Sửa lại trong student_model.py
def update_score(data):
    """
    Cập nhật một bản ghi điểm đã có trong bảng `scores`.

    Args:
        data (dict): Một dictionary chứa các thông tin cần thiết:
                     'student_id', 'class_subject_id', 'year',
                     'midterm_score', 'final_score', 'process_score'.
    """
    required_keys = ['student_id', 'class_subject_id', 'year', 'midterm_score', 'final_score', 'process_score']
    if not all(key in data for key in required_keys):
        print("Lỗi: Thiếu thông tin cần thiết để cập nhật điểm.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE scores 
            SET midterm_score = ?, final_score = ?, process_score = ?
            WHERE student_id = ? AND class_subject_id = ? AND year = ?
        """, (
            data.get("midterm_score"),
            data.get("final_score"),
            data.get("process_score"),
            data.get("student_id"),
            data.get("class_subject_id"),
            data.get("year")
        ))
        conn.commit()

        # rowcount sẽ cho biết có bao nhiêu dòng đã được cập nhật
        if cursor.rowcount == 0:
            print(f"⚠️ Không tìm thấy bản ghi điểm nào để cập nhật cho SV: {data.get('student_id')}.")
            # Ở đây bạn có thể cân nhắc gọi hàm add_score nếu không tìm thấy
            # add_score(data)
        else:
            print(f"✅ Đã cập nhật điểm thành công cho sinh viên ID: {data.get('student_id')}")

    except sqlite3.Error as e:
        print(f"❌ Lỗi CSDL khi cập nhật điểm: {e}")
    finally:
        conn.close()

def get_subjects_for_teacher_in_semester(teacher_id, academic_year_id, semester_id):
    """
    Lấy danh sách các môn học (ID và tên) mà một giáo viên dạy
    cho một danh sách các lớp.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Dùng Row Factory cho dễ
    cursor = conn.cursor()

    query = f"""
        SELECT DISTINCT s.subject_id, s.subject_name, ta.semester_id
        FROM teacher_assignments ta
        JOIN subjects s ON ta.subject_id = s.subject_id
        WHERE ta.teacher_id = ? 
        AND ta.academic_year_id = ?  -- Lọc theo năm học
        AND ta.semester_id = ?       -- Lọc theo học kỳ
    """

    params = (teacher_id, academic_year_id, semester_id)
    cursor.execute(query, params)

    subjects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return subjects


def get_classes_for_subject_in_semester(teacher_id, academic_year_id, semester_id, subject_id):
    """
    Lấy danh sách các lớp (class_name) và ID môn học của lớp (class_subject_id)
    mà một giáo viên dạy một môn cụ thể trong một học kỳ.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- ĐÂY LÀ CÂU TRUY VẤN CẦN SỬA ---
    query = """
        SELECT DISTINCT
            c.class_name,
            cs.class_subject_id -- <<< DÒNG QUAN TRỌNG NHẤT
        FROM 
            teacher_assignments ta
        JOIN 
            classes c ON ta.class_id = c.class_id
        JOIN
            class_subjects cs ON ta.class_id = cs.class_id 
                             AND ta.subject_id = cs.subject_id 
                             AND ta.semester_id = cs.semester_id
        WHERE
            ta.teacher_id = ? 
            AND ta.academic_year_id = ?
            AND ta.semester_id = ?
            AND ta.subject_id = ?
        ORDER BY
            c.class_name;
    """
    # --- KẾT THÚC SỬA LỖI ---

    params = (teacher_id, academic_year_id, semester_id, subject_id)

    try:
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in get_classes_for_subject_in_semester: {e}")
        rows = []
    finally:
        conn.close()

    return rows

# lấy điểm cuối kỳ các lớp
def get_scores_for_boxplot(teacher_id, academic_year_id, semester_id, subject_id):
    """Lấy điểm cuối kỳ của tất cả các lớp cho một môn học cụ thể."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
        SELECT c.class_name, sc.final_score
        FROM teacher_assignments ta
        JOIN classes c ON ta.class_id = c.class_id
        JOIN class_subjects cs ON ta.class_id = cs.class_id AND ta.subject_id = cs.subject_id AND ta.semester_id = cs.semester_id
        LEFT JOIN scores sc ON cs.class_subject_id = sc.class_subject_id AND sc.year = (SELECT start_year FROM academic_years WHERE academic_year_id = ta.academic_year_id)
        WHERE ta.teacher_id = ? AND ta.academic_year_id = ? AND ta.semester_id = ? AND ta.subject_id = ?
          AND sc.final_score IS NOT NULL;
    """
    params = (teacher_id, academic_year_id, semester_id, subject_id)
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# So sánh nhanh tỉ lệ sinh viên đạt yêu cầu giữa tất cả các lớp học phần.
def get_pass_fail_stats(teacher_id, academic_year_id, semester_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
        SELECT
            c.class_name,
            COUNT(sc.score_id) AS total_students,
            SUM(CASE WHEN sc.final_score >= 5.0 THEN 1 ELSE 0 END) AS passed_students
        FROM teacher_assignments ta
        JOIN classes c ON ta.class_id = c.class_id
        JOIN class_subjects cs ON ta.class_id = cs.class_id AND ta.subject_id = cs.subject_id AND ta.semester_id = cs.semester_id
        LEFT JOIN scores sc ON cs.class_subject_id = sc.class_subject_id AND sc.year = (SELECT start_year FROM academic_years WHERE academic_year_id = ta.academic_year_id)
        WHERE ta.teacher_id = ? AND ta.academic_year_id = ? AND ta.semester_id = ?
        GROUP BY c.class_name
        HAVING total_students > 0;
    """
    params = (teacher_id, academic_year_id, semester_id)
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# Xem chi tiết phân phối điểm cuối kỳ của một lớp học phần cụ thể.
def get_scores_for_histogram(class_subject_id, year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT final_score FROM scores WHERE class_subject_id = ? AND year = ? AND final_score IS NOT NULL;"
    params = (class_subject_id, year)
    cursor.execute(query, params)
    # Trả về một list các con số
    scores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return scores

# So sánh điểm quá trình trung bình và điểm cuối kỳ trung bình của tất cả các lớp.
def get_avg_scores_by_class(teacher_id, academic_year_id, semester_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
           SELECT 
               c.class_name, 
               AVG(sc.process_score) as avg_process_score,
               AVG(sc.final_score) as avg_final_score
           FROM 
               teacher_assignments ta
           JOIN 
               classes c ON ta.class_id = c.class_id
           JOIN 
               class_subjects cs ON ta.class_id = cs.class_id 
                                AND ta.subject_id = cs.subject_id 
                                AND ta.semester_id = cs.semester_id
           LEFT JOIN 
               scores sc ON cs.class_subject_id = sc.class_subject_id
                         AND sc.year = (SELECT start_year FROM academic_years WHERE academic_year_id = ta.academic_year_id)
           WHERE 
               ta.teacher_id = ? 
               AND ta.academic_year_id = ? 
               AND ta.semester_id = ?
           GROUP BY 
               c.class_name;
       """
    params = (teacher_id, academic_year_id, semester_id)
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows