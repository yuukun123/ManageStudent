import sqlite3

import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'student_management.db'))

def get_all_faculties():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT faculty_id, faculty_name FROM faculties")
    return cursor.fetchall()  # ✅ [(1, 'IT'), (2, 'Business')]
