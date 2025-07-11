import sqlite3
from datetime import datetime

def generate_academic_years_if_needed():
    db_path = "data/student_management.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    this_year = datetime.now().year

    # Kiểm tra tổng số năm học hiện tại
    cursor.execute("SELECT COUNT(*) FROM academic_years")
    total_years = cursor.fetchone()[0]
    if total_years > 10:
        print("⚠️ Đã đủ số năm học, không thêm nữa")
        conn.close()
        return

    # Kiểm tra năm học lớn nhất
    cursor.execute("SELECT MAX(start_year) FROM academic_years")
    result = cursor.fetchone()
    max_year = result[0] if result[0] else 0

    if max_year < this_year:
        start_year = this_year
        for i in range(3):  # sinh 3 năm học tiếp theo
            end_year = start_year + 1
            cursor.execute("""
                INSERT INTO academic_years (start_year, end_year)
                VALUES (?, ?)
            """, (start_year, end_year))
            print(f"✅ Đã thêm năm học {start_year}-{end_year}")
            start_year += 1

        conn.commit()
    else:
        print("✅ Năm học đã cập nhật, không cần thêm mới.")

    conn.close()
