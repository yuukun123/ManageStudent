import sqlite3

DB_PATH = "data/student_management.db"

def get_all_majors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT major_id, major_name FROM majors")
    majors = cursor.fetchall()
    conn.close()
    return majors  # Trả về list of tuples: (1, "Công nghệ thông tin")
