from datetime import datetime, timezone

from core.database import transaction


class AcademicError(ValueError):
    pass


def create_department(code: str, name: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    try:
        with transaction() as connection:
            return connection.execute(
                "INSERT INTO departments (code, name, is_active, created_at, updated_at) VALUES (?, ?, 1, ?, ?)",
                (code.strip().upper(), name.strip(), now, now),
            ).lastrowid
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise AcademicError("Department code or name already exists") from exc
        raise


def create_course(department_id: int, course_code: str, course_name: str, units: int, description: str | None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with transaction() as connection:
        if not connection.execute("SELECT 1 FROM departments WHERE id = ? AND is_active = 1", (department_id,)).fetchone():
            raise AcademicError("Active department not found")
        try:
            return connection.execute(
                "INSERT INTO courses (department_id, course_code, course_name, units, description, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                (department_id, course_code.strip().upper(), course_name.strip(), units, description, now, now),
            ).lastrowid
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise AcademicError("Course code already exists") from exc
            raise
