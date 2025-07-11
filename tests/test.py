import sqlite3

# Kết nối tới cơ sở dữ liệu
conn = sqlite3.connect('../src/data/student_management.db')
cursor = conn.cursor()

# Câu lệnh SQL để cập nhật giá trị
# Ví dụ: Đổi tên người dùng có ID 1 thành "Tên Mới"
sql_query = """
UPDATE subjects
SET midterm_weight = 0.5, final_weight = 0.5
WHERE subject_id = 2;
"""

# Thực thi câu lệnh
try:
    cursor.execute(sql_query)
    conn.commit()  # Lưu các thay đổi
    print("Cập nhật thành công!")
except sqlite3.Error as e:
    print(f"Lỗi: {e}")
finally:
    # Đóng kết nối
    conn.close()