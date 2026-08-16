import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from core.database import get_connection
from core.security import hash_password
from migrations.migrate_v2 import run_migrations


@contextmanager
def temporary_database():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "university.db"
        previous = os.environ.get("UNIVERSITY_DB_PATH")
        os.environ["UNIVERSITY_DB_PATH"] = str(path)
        run_migrations(path)
        try:
            yield
        finally:
            if previous is None:
                os.environ.pop("UNIVERSITY_DB_PATH", None)
            else:
                os.environ["UNIVERSITY_DB_PATH"] = previous


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_student(username="student", status="active"):
    timestamp = now()
    with get_connection() as connection:
        department_id = connection.execute("SELECT id FROM departments WHERE code = 'GENERAL'").fetchone()[0]
        user_id = connection.execute("INSERT INTO users (username, full_name, password_hash, role, is_active, created_at, updated_at) VALUES (?, ?, ?, 'student', 1, ?, ?)", (username, username.title(), hash_password("secret"), timestamp, timestamp)).lastrowid
        student_id = connection.execute("INSERT INTO students (user_id, student_number, department_id, major, entry_year, academic_status, created_at, updated_at) VALUES (?, ?, ?, 'Computer Engineering', 1405, ?, ?, ?)", (user_id, f"S-{user_id}", department_id, status, timestamp, timestamp)).lastrowid
        return user_id, student_id


def seed_professor(username="professor"):
    timestamp = now()
    with get_connection() as connection:
        department_id = connection.execute("SELECT id FROM departments WHERE code = 'GENERAL'").fetchone()[0]
        user_id = connection.execute("INSERT INTO users (username, full_name, password_hash, role, is_active, created_at, updated_at) VALUES (?, ?, ?, 'professor', 1, ?, ?)", (username, username.title(), hash_password("secret"), timestamp, timestamp)).lastrowid
        professor_id = connection.execute("INSERT INTO professors (user_id, personnel_code, department_id, employment_status, created_at, updated_at) VALUES (?, ?, ?, 'active', ?, ?)", (user_id, f"P-{user_id}", department_id, timestamp, timestamp)).lastrowid
        return user_id, professor_id


def seed_section(code="CE101", units=3, capacity=30, professor_id=None):
    timestamp = now()
    with get_connection() as connection:
        department_id = connection.execute("SELECT id FROM departments WHERE code = 'GENERAL'").fetchone()[0]
        semester_id = connection.execute("SELECT id FROM semesters WHERE status = 'active'").fetchone()[0]
        classroom_id = connection.execute("SELECT id FROM classrooms LIMIT 1").fetchone()[0]
        course_id = connection.execute("INSERT INTO courses (course_code, course_name, units, teacher, capacity, department_id, is_active, created_at, updated_at) VALUES (?, ?, ?, '', ?, ?, 1, ?, ?)", (code, code, units, capacity, department_id, timestamp, timestamp)).lastrowid
        section_id = connection.execute("INSERT INTO course_sections (course_id, semester_id, professor_id, classroom_id, section_number, capacity, status, created_at, updated_at) VALUES (?, ?, ?, ?, '01', ?, 'open', ?, ?)", (course_id, semester_id, professor_id, classroom_id, capacity, timestamp, timestamp)).lastrowid
        return course_id, section_id
