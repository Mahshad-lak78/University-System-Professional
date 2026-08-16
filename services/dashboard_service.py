from database_connection import get_connection


def get_student_dashboard(user_id: int):
    with get_connection() as connection:
        student = connection.execute(
            "SELECT students.*, users.full_name, users.username, departments.name AS department_name FROM students JOIN users ON users.id = students.user_id LEFT JOIN departments ON departments.id = students.department_id WHERE students.user_id = ?",
            (user_id,),
        ).fetchone()
        if student is None:
            return None
        courses = connection.execute(
            """SELECT cs.id, c.course_code, c.course_name, c.units, COALESCE(u.full_name, 'تخصیص داده نشده') AS teacher,
                      cs.capacity, COUNT(active_e.id) AS enrolled_count
               FROM enrollments e JOIN course_sections cs ON cs.id = e.course_section_id
               JOIN courses c ON c.id = cs.course_id
               LEFT JOIN professors p ON p.id = cs.professor_id LEFT JOIN users u ON u.id = p.user_id
               LEFT JOIN enrollments active_e ON active_e.course_section_id = cs.id AND active_e.status = 'enrolled'
               WHERE e.student_id = ? AND e.status = 'enrolled'
               GROUP BY cs.id ORDER BY c.course_code""",
            (student["id"],),
        ).fetchall()
        return student, courses
