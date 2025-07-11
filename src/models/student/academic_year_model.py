import sqlite3

DB_PATH = "data/student_management.db"

def get_all_academic_years():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT academic_year_id, start_year, end_year FROM academic_years")
    academic_years = cursor.fetchall()
    conn.close()
    return academic_years  # Trả về list of tuples