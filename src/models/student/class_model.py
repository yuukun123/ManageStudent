import sqlite3

DB_PATH = "data/student_management.db"

def get_all_classrooms():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT class_id, class_name FROM classes")
    classrooms = cursor.fetchall()
    conn.close()
    return classrooms  # Trả về list of tuples