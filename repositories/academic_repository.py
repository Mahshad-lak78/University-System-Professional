from core.database import get_connection


def list_departments():
    with get_connection() as connection:
        return connection.execute("SELECT * FROM departments WHERE is_active = 1 ORDER BY name").fetchall()


def list_current_sections():
    with get_connection() as connection:
        return connection.execute(
            """SELECT cs.*, c.course_code, c.course_name, c.units, sem.code AS semester_code,
                      COALESCE(u.full_name, 'Unassigned') AS professor_name,
                      COUNT(e.id) AS enrolled_count
               FROM course_sections cs
               JOIN courses c ON c.id = cs.course_id
               JOIN semesters sem ON sem.id = cs.semester_id
               LEFT JOIN professors p ON p.id = cs.professor_id
               LEFT JOIN users u ON u.id = p.user_id
               LEFT JOIN enrollments e ON e.course_section_id = cs.id AND e.status = 'enrolled'
               WHERE sem.status = 'active'
               GROUP BY cs.id ORDER BY c.course_code, cs.section_number"""
        ).fetchall()


def student_enrollments(user_id: int):
    with get_connection() as connection:
        return connection.execute(
            """SELECT e.*, c.course_code, c.course_name, c.units, sem.code AS semester_code,
                      g.score, g.status AS grade_status
               FROM enrollments e
               JOIN students st ON st.id = e.student_id
               JOIN course_sections cs ON cs.id = e.course_section_id
               JOIN courses c ON c.id = cs.course_id
               JOIN semesters sem ON sem.id = cs.semester_id
               LEFT JOIN grades g ON g.enrollment_id = e.id
               WHERE st.user_id = ? ORDER BY sem.start_date DESC, c.course_code""",
            (user_id,),
        ).fetchall()


def dashboard_counts():
    with get_connection() as connection:
        return {
            "students": connection.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "professors": connection.execute("SELECT COUNT(*) FROM professors").fetchone()[0],
            "courses": connection.execute("SELECT COUNT(*) FROM courses WHERE is_active = 1").fetchone()[0],
            "enrollments": connection.execute("SELECT COUNT(*) FROM enrollments WHERE status = 'enrolled'").fetchone()[0],
        }
