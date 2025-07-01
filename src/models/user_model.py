import sqlite3
import hashlib

DB_PATH = "data/student_management.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
    import os
    print(f"DEBUG: Looking for DB at: {os.path.abspath(DB_PATH)}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? AND password_hash = ?
    """, (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("✅ Login success!")
        return True
    else:
        print("❌ Login failed!")
        return False

def get_all_users():
    conn = sqlite3.connect('data/student_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

if __name__ == "__main__":
    # Ví dụ thêm user
    add_user("admin", "admin123")


