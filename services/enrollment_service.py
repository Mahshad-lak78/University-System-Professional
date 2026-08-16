from database_connection import get_connection


def enroll_course(student_id: int, course_id: int):
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id)
        ).fetchone()
        if exists:
            return {"ok": False, "message": "این درس قبلاً انتخاب شده است."}

        course = connection.execute("SELECT capacity FROM courses WHERE id = ?", (course_id,)).fetchone()
        if course is None:
            return {"ok": False, "message": "درس پیدا نشد."}
        if course["capacity"] <= 0:
            return {"ok": False, "message": "ظرفیت درس تکمیل است."}

        connection.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
        connection.execute("UPDATE courses SET capacity = capacity - 1 WHERE id = ?", (course_id,))
        return {"ok": True, "message": "انتخاب واحد با موفقیت انجام شد."}


def get_student_courses(student_id: int):
    with get_connection() as connection:
        return connection.execute(
            """SELECT courses.* FROM courses JOIN enrollments ON courses.id = enrollments.course_id
               WHERE enrollments.student_id = ? ORDER BY courses.course_code""",
            (student_id,),
        ).fetchall()


def drop_course(student_id: int, course_id: int):
    with get_connection() as connection:
        enrollment = connection.execute(
            "SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id)
        ).fetchone()
        if enrollment is None:
            return {"ok": False, "message": "این درس برای دانشجو ثبت نشده است."}
        connection.execute("DELETE FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        connection.execute("UPDATE courses SET capacity = capacity + 1 WHERE id = ?", (course_id,))
        return {"ok": True, "message": "درس با موفقیت حذف شد."}
