from datetime import datetime, timezone
import sqlite3

from core.database import transaction
from database_connection import get_connection



class EnrollmentError(ValueError):
    pass





def enroll_authenticated_student(user_id: int, course_section_id: int) -> int:

    now = datetime.now(timezone.utc).isoformat()


    with transaction() as connection:


        student = connection.execute(
            """
            SELECT *
            FROM students
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()



        if student is None:
            raise EnrollmentError(
                "Student profile not found"
            )



        if student["academic_status"] != "active":
            raise EnrollmentError(
                "Student is not eligible for enrollment"
            )




        section = connection.execute(
            """
            SELECT 
                cs.*,
                c.id AS course_id,
                c.units,
                c.is_active AS course_active,
                s.status AS semester_status,
                s.max_units_default,
                s.registration_start,
                s.registration_end

            FROM course_sections cs

            JOIN courses c
            ON c.id = cs.course_id

            JOIN semesters s
            ON s.id = cs.semester_id

            WHERE cs.id = ?
            """,
            (course_section_id,)
        ).fetchone()



        if section is None:
            raise EnrollmentError(
                "Course section not found"
            )



        if section["status"] != "open":
            raise EnrollmentError(
                "Course section is not available"
            )



        if not section["course_active"]:
            raise EnrollmentError(
                "Course is inactive"
            )



        if section["semester_status"] != "active":
            raise EnrollmentError(
                "Semester is not active"
            )




        today = datetime.now(
            timezone.utc
        ).date().isoformat()



        if not (
            section["registration_start"]
            <= today
            <= section["registration_end"]
        ):
            raise EnrollmentError(
                "Registration is not currently open"
            )





        existing = connection.execute(
            """
            SELECT *
            FROM enrollments

            WHERE student_id = ?
            AND course_section_id = ?

            ORDER BY id DESC
            LIMIT 1
            """,
            (
                student["id"],
                course_section_id
            )
        ).fetchone()



        # اگر قبلا فعال بوده
        if existing and existing["status"] == "enrolled":

            raise EnrollmentError(
                "این درس قبلاً انتخاب شده است."
            )





        # اگر قبلا حذف شده بوده، دوباره فعال کن
        if existing and existing["status"] == "dropped":


            connection.execute(
                """
                UPDATE enrollments

                SET status='enrolled',
                    dropped_at=NULL,
                    enrolled_at=?,
                    updated_at=?

                WHERE id=?
                """,
                (
                    now,
                    now,
                    existing["id"]
                )
            )


            return existing["id"]







        # چک انتخاب همان درس در ترم
        same_course = connection.execute(
            """
            SELECT 1

            FROM enrollments e

            JOIN course_sections cs
            ON cs.id = e.course_section_id


            WHERE e.student_id=?

            AND cs.semester_id=?

            AND cs.course_id=?

            AND e.status='enrolled'
            """,
            (
                student["id"],
                section["semester_id"],
                section["course_id"]
            )
        ).fetchone()



        if same_course:

            raise EnrollmentError(
                "این درس را قبلاً در این ترم انتخاب کرده‌اید."
            )







        enrolled_count = connection.execute(
            """
            SELECT COUNT(*)

            FROM enrollments

            WHERE course_section_id=?

            AND status='enrolled'
            """,
            (course_section_id,)
        ).fetchone()[0]




        if enrolled_count >= section["capacity"]:

            raise EnrollmentError(
                "ظرفیت کلاس تکمیل شده است."
            )







        try:

            result = connection.execute(
                """
                INSERT INTO enrollments
                (
                    student_id,
                    course_id,
                    course_section_id,
                    registered_units,
                    status,
                    enrolled_at,
                    created_at,
                    updated_at
                )

                VALUES
                (?,?,?,?,?,?,?,?)
                """,
                (
                    student["id"],
                    section["course_id"],
                    course_section_id,
                    section["units"],
                    "enrolled",
                    now,
                    now,
                    now
                )
            )


            return result.lastrowid



        except sqlite3.IntegrityError as exc:

            raise EnrollmentError(
                "خطا در ثبت انتخاب واحد"
            ) from exc







def drop_authenticated_student(
    user_id:int,
    course_section_id:int
):


    now=datetime.now(
        timezone.utc
    ).isoformat()



    with transaction() as connection:


        student=connection.execute(
            """
            SELECT id
            FROM students
            WHERE user_id=?
            """,
            (user_id,)
        ).fetchone()



        if student is None:

            raise EnrollmentError(
                "Student profile not found"
            )



        updated=connection.execute(
            """
            UPDATE enrollments

            SET status='dropped',
                dropped_at=?,
                updated_at=?

            WHERE student_id=?

            AND course_section_id=?

            AND status='enrolled'
            """,
            (
                now,
                now,
                student["id"],
                course_section_id
            )
        ).rowcount



        if not updated:

            raise EnrollmentError(
                "Active enrollment not found"
            )







def get_enrollments_for_student(student_id:int):


    with get_connection() as connection:


        return connection.execute(
            """
            SELECT
                e.id,
                e.status,
                e.registered_units,
                cs.id AS course_section_id,
                c.course_code,
                c.course_name,
                sem.code AS semester_code

            FROM enrollments e

            JOIN course_sections cs
            ON cs.id=e.course_section_id

            JOIN courses c
            ON c.id=cs.course_id

            JOIN semesters sem
            ON sem.id=cs.semester_id

            WHERE e.student_id=?

            ORDER BY sem.start_date DESC,
            c.course_code
            """,
            (student_id,)
        ).fetchall()