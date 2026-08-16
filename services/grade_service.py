from datetime import datetime, timezone

from core.database import transaction


class GradeError(ValueError):
    pass


def upsert_grade(professor_user_id: int, enrollment_id: int, score: float, publish: bool) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with transaction() as connection:
        professor = connection.execute("SELECT id FROM professors WHERE user_id = ? AND employment_status = 'active'", (professor_user_id,)).fetchone()
        if professor is None:
            raise GradeError("Professor profile not found")
        enrollment = connection.execute("SELECT e.id FROM enrollments e JOIN course_sections cs ON cs.id = e.course_section_id WHERE e.id = ? AND cs.professor_id = ?", (enrollment_id, professor["id"])).fetchone()
        if enrollment is None:
            raise GradeError("You are not assigned to this enrollment")
        status = "published" if publish else "draft"
        published_at = now if publish else None
        existing = connection.execute("SELECT id FROM grades WHERE enrollment_id = ?", (enrollment_id,)).fetchone()
        if existing:
            connection.execute("UPDATE grades SET score = ?, status = ?, graded_by_professor_id = ?, published_at = ?, updated_at = ? WHERE id = ?", (score, status, professor["id"], published_at, now, existing["id"]))
            return existing["id"]
        return connection.execute("INSERT INTO grades (enrollment_id, score, status, graded_by_professor_id, published_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (enrollment_id, score, status, professor["id"], published_at, now, now)).lastrowid
