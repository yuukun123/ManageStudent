import sqlite3

import os
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'student_management.db'))

def get_classes_by_faculty_id(faculty_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT class_name
            FROM classes
            WHERE faculty_id = ?
        """, (faculty_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print("❌ Error in get_classes_by_faculty_id:", e)
        return []
    finally:
        conn.close()









