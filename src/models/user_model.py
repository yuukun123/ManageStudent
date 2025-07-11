import sqlite3
import hashlib
from werkzeug.security import check_password_hash

DB_PATH = "data/student_management.db"

def hash_password(password):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash) VALUES (?, ?)
        """, (username, hash_password(password)))
        conn.commit()
        print(f"✅ User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"⚠ Username '{username}' already exists.")
    finally:
        conn.close()


def check_login(username, password):
    """
    Checks user credentials against the database correctly.
    Returns user info dictionary on success, None on failure.
    """
    conn = sqlite3.connect(DB_PATH)
    # Trả về kết quả dưới dạng dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Bước 1: Lấy thông tin người dùng bằng username
    # Chúng ta chỉ cần lấy password_hash để kiểm tra
    cursor.execute("""
        SELECT id, username, password_hash, role, full_name, faculty_id
        FROM users 
        WHERE username = ?
    """, (username,))

    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        # Bước 2: Dùng check_password_hash để so sánh mật khẩu người dùng nhập
        # với chuỗi hash đã lưu trong DB.
        stored_password_hash = user_data['password_hash']

        if check_password_hash(stored_password_hash, password):
            print(f"✅ Login success for user '{username}' with role '{user_data['role']}'.")
            # Trả về một dictionary chứa thông tin người dùng, rất hữu ích cho ứng dụng
            return dict(user_data)
        else:
            print(f"❌ Login failed for user '{username}': Incorrect password.")
            return None
    else:
        print(f"❌ Login failed: User '{username}' not found.")
        return None
# def check_login(username, password):
#     import os
#     print(f"DEBUG: Looking for DB at: {os.path.abspath(DB_PATH)}")
#
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT * FROM users WHERE username = ? AND password_hash = ?
#     """, (username, hash_password(password)))
#     user = cursor.fetchone()
#     conn.close()
#
#     if user:
#         print("✅ Login success!")
#         return True
#     else:
#         print("❌ Login failed!")
#         return False

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

import sqlite3


def get_user_by_username(username: str):
    """Trả về thông tin người dùng cơ bản từ bảng users."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_teacher_context(username: str):
    """
    Lấy thông tin phân quyền (faculties + classes) cho giáo viên theo username.
    Trả về None nếu không tìm thấy hoặc không có phân công.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT
            u.id AS teacher_id,
            u.full_name AS teacher_name,
            c.class_id,
            c.class_name,
            f.faculty_id,
            f.faculty_name
        FROM users u
        JOIN teacher_assignments ta ON u.id = ta.teacher_id
        JOIN classes c ON ta.class_id = c.class_id
        JOIN faculties f ON c.faculty_id = f.faculty_id
        WHERE u.username = ?
    """
    cursor.execute(query, (username,))
    assignments = [dict(row) for row in cursor.fetchall()]
    print("[DEBUG] Query result:", assignments)
    conn.close()

    if not assignments:
        return None

    teacher_id = assignments[0]['teacher_id']
    teacher_name = assignments[0]['teacher_name']
    allowed_faculties = {(row['faculty_id'], row['faculty_name']) for row in assignments}
    allowed_classes = {(row['class_id'], row['class_name'], row['faculty_id']) for row in assignments}

    return {
        "teacher_id": teacher_id,
        "teacher_name": teacher_name,
        "faculties": sorted(list(allowed_faculties), key=lambda x: x[1]),
        "classes": sorted(list(allowed_classes), key=lambda x: x[1])
    }