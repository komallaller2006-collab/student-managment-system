"""
Database Service for Student Management System
Handles SQLite database initialization, admin authentication, student records, and tokens.
"""

import sqlite3
import os
import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "students.db")


def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Admins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Students table with secure token
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            father_name TEXT DEFAULT '',
            dob TEXT DEFAULT '',
            address TEXT DEFAULT '',
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Assignments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no) ON DELETE CASCADE
        )
    """)

    # Default Admin account (admin / admin123)
    cursor.execute("SELECT id FROM admins WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("admin123")
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ("admin", hashed_pw))

    conn.commit()
    conn.close()


def verify_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username.strip(),))
    admin = cursor.fetchone()
    conn.close()
    if admin and check_password_hash(admin["password_hash"], password):
        return True
    return False


def generate_student_token():
    return secrets.token_urlsafe(24)


def create_or_update_student(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    roll_no = data["roll_no"].strip().upper()

    cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
    existing = cursor.fetchone()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existing:
        token = existing["token"]
        cursor.execute("""
            UPDATE students SET
                name = ?,
                class_name = ?,
                email = ?,
                phone = ?,
                father_name = ?,
                dob = ?,
                address = ?,
                updated_at = ?
            WHERE roll_no = ?
        """, (
            data.get("name", "").strip(),
            data.get("class_name", "").strip(),
            data.get("email", "").strip(),
            data.get("phone", "").strip(),
            data.get("father_name", "").strip(),
            data.get("dob", "").strip(),
            data.get("address", "").strip(),
            now_str,
            roll_no
        ))
    else:
        token = generate_student_token()
        cursor.execute("""
            INSERT INTO students (
                roll_no, name, class_name, email, phone, father_name, dob, address, token, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            roll_no,
            data.get("name", "").strip(),
            data.get("class_name", "").strip(),
            data.get("email", "").strip(),
            data.get("phone", "").strip(),
            data.get("father_name", "").strip(),
            data.get("dob", "").strip(),
            data.get("address", "").strip(),
            token,
            now_str,
            now_str
        ))

    conn.commit()
    conn.close()
    return roll_no, token


def get_student(roll_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no.strip().upper(),))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None


def validate_student_access(roll_no, token):
    """Returns True if the given token matches the roll_no in database."""
    if not roll_no or not token:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE roll_no = ? AND token = ?", (roll_no.strip().upper(), token.strip()))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, COUNT(a.id) as assignment_count 
        FROM students s 
        LEFT JOIN assignments a ON s.roll_no = a.roll_no 
        GROUP BY s.id 
        ORDER BY s.updated_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_student(roll_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    roll_no = roll_no.strip().upper()
    cursor.execute("DELETE FROM assignments WHERE roll_no = ?", (roll_no,))
    cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
    conn.commit()
    conn.close()


def log_assignment(roll_no, filename, original_name, file_path, file_size):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assignments (roll_no, filename, original_name, file_path, file_size)
        VALUES (?, ?, ?, ?, ?)
    """, (roll_no.strip().upper(), filename, original_name, file_path, file_size))
    conn.commit()
    conn.close()


def get_student_assignments(roll_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assignments 
        WHERE roll_no = ? 
        ORDER BY upload_time DESC
    """, (roll_no.strip().upper(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_assignments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, s.name as student_name, s.class_name 
        FROM assignments a
        JOIN students s ON a.roll_no = s.roll_no
        ORDER BY a.upload_time DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
