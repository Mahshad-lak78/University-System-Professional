from datetime import datetime, timezone

from core.database import transaction
from core.security import hash_password, verify_password
from repositories.university_repository import get_user_by_username


def authenticate(username: str, password: str):
    user = get_user_by_username(username)
    if user is None or not user["is_active"] or not verify_password(password, user["password_hash"]):
        return None
    with transaction() as connection:
        connection.execute("UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), user["id"]))
    return user


def register_student(fullname: str, username: str, password: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with transaction() as connection:
        if connection.execute("SELECT 1 FROM users WHERE username = ?", (username.strip(),)).fetchone():
            raise ValueError("username already exists")
        department = connection.execute("SELECT id FROM departments WHERE code = 'GENERAL'").fetchone()
        if department is None:
            raise RuntimeError("database is not initialized")
        user_id = connection.execute("INSERT INTO users (username, role, full_name, password_hash, is_active, created_at, updated_at) VALUES (?, 'student', ?, ?, 1, ?, ?)", (username.strip(), fullname.strip(), hash_password(password), now, now)).lastrowid
        student_number = f"S{1405}{user_id:05d}"
        connection.execute("INSERT INTO students (user_id, student_number, department_id, major, entry_year, academic_status, created_at, updated_at) VALUES (?, ?, ?, 'Undeclared', 1405, 'active', ?, ?)", (user_id, student_number, department["id"], now, now))
        return user_id
