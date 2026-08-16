from core.database import get_connection


def get_user_by_id(user_id: int):
    with get_connection() as connection:
        return connection.execute("SELECT id, username, full_name, role, is_active FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(username: str):
    with get_connection() as connection:
        return connection.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()


def get_student_by_user_id(user_id: int):
    with get_connection() as connection:
        return connection.execute("SELECT students.*, users.full_name, users.username FROM students JOIN users ON users.id = students.user_id WHERE students.user_id = ?", (user_id,)).fetchone()


def get_professor_by_user_id(user_id: int):
    with get_connection() as connection:
        return connection.execute("SELECT * FROM professors WHERE user_id = ?", (user_id,)).fetchone()
