import os
import sqlite3
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Optional, List
import config

class ValidationError(Exception):
    pass

class DatabaseError(Exception):
    pass

class AuthenticationError(Exception):
    pass

@dataclass
class StudentRecord:
    id: Optional[int] = None
    name: str = ''
    age: Optional[int] = None
    grade: str = ''
    photo: str = ''

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError('Student name is required')
        if self.age is not None and self.age < 0:
            raise ValidationError('Age cannot be negative')

    @classmethod
    @contextmanager
    def _db_connection(cls):
        db_path = getattr(config, 'DATABASE_PATH', 'students.db')
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    def create_table(cls) -> None:
        with cls._db_connection() as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    grade TEXT,
                    photo TEXT
                )
                '''
            )
            conn.commit()

    def save(self) -> 'StudentRecord':
        self.validate()
        with self._db_connection() as conn:
            if self.id is None:
                cursor = conn.execute(
                    'INSERT INTO students (name, age, grade, photo) VALUES (?, ?, ?, ?)',
                    (self.name, self.age, self.grade, self.photo),
                )
                self.id = cursor.lastrowid
            else:
                conn.execute(
                    'UPDATE students SET name = ?, age = ?, grade = ?, photo = ? WHERE id = ?',
                    (self.name, self.age, self.grade, self.photo, self.id),
                )
            conn.commit()
        return self

    def delete(self) -> None:
        if self.id is None:
            raise DatabaseError('Student does not exist in database')
        with self._db_connection() as conn:
            conn.execute('DELETE FROM students WHERE id = ?', (self.id,))
            conn.commit()
            self.id = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'StudentRecord':
        return cls(
            id=row['id'],
            name=row['name'] or '',
            age=row['age'] if row['age'] is not None else None,
            grade=row['grade'] or '',
            photo=row['photo'] or '',
        )

    @classmethod
    def get_by_id(cls, student_id: int) -> 'StudentRecord':
        with cls._db_connection() as conn:
            row = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
            if row is None:
                raise DatabaseError(f'Student with id {student_id} not found')
            return cls.from_row(row)

    @classmethod
    def list_all(cls) -> List['StudentRecord']:
        with cls._db_connection() as conn:
            rows = conn.execute('SELECT * FROM students ORDER BY name COLLATE NOCASE').fetchall()
            return [cls.from_row(row) for row in rows]

    @classmethod
    def search(cls, query: str) -> List['StudentRecord']:
        query_value = f'%{query.strip()}%'
        with cls._db_connection() as conn:
            rows = conn.execute(
                'SELECT * FROM students WHERE name LIKE ? OR grade LIKE ? ORDER BY name COLLATE NOCASE',
                (query_value, query_value),
            ).fetchall()
            return [cls.from_row(row) for row in rows]

class studentmanagementsystem:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            config.DATABASE_PATH = db_path
        self.db_path = getattr(config, 'DATABASE_PATH', 'students.db')
        StudentRecord.create_table()

    def authenticate_user(self, username: str, password: str) -> bool:
        if username == getattr(config, 'DEFAULT_ADMIN_USERNAME', 'admin') and password == getattr(config, 'DEFAULT_ADMIN_PASSWORD', 'admin123'):
            return True
        return False

    def get_students(self, query: Optional[str] = None) -> List[StudentRecord]:
        return StudentRecord.search(query) if query else StudentRecord.list_all()

    def get_student(self, student_id: int) -> StudentRecord:
        return StudentRecord.get_by_id(student_id)

    def create_student(self, data: dict) -> StudentRecord:
        try:
            age = int(data.get('age')) if data.get('age') not in (None, '') else None
        except ValueError:
            raise ValidationError('Age must be a number')
        student = StudentRecord(
            name=data.get('name', '').strip(),
            age=age,
            grade=data.get('grade', '').strip(),
            photo=data.get('photo', '').strip(),
        )
        return student.save()

    def update_student(self, student_id: int, data: dict) -> StudentRecord:
        student = self.get_student(student_id)
        if 'name' in data:
            student.name = data.get('name', student.name).strip()
        if 'age' in data:
            try:
                student.age = int(data.get('age')) if data.get('age') not in (None, '') else None
            except ValueError:
                raise ValidationError('Age must be a number')
        if 'grade' in data:
            student.grade = data.get('grade', student.grade).strip()
        if 'photo' in data:
            student.photo = data.get('photo', student.photo).strip()
        return student.save()

    def delete_student(self, student_id: int) -> bool:
        student = self.get_student(student_id)
        student.delete()
        return True
    