from database_connection import get_connection


def create_course(
    course_code: str,
    course_name: str,
    units: int,
    teacher: str,
    capacity: int,
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO courses
            (
                course_code,
                course_name,
                units,
                teacher,
                capacity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                course_code,
                course_name,
                units,
                teacher,
                capacity,
            ),
        )

        course_id = cursor.lastrowid

        return connection.execute(
            """
            SELECT *
            FROM courses
            WHERE id = ?
            """,
            (course_id,),
        ).fetchone()


def get_courses():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM courses
            ORDER BY course_code
            """
        ).fetchall()


def get_available_sections():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                cs.id,
                c.course_code,
                c.course_name,
                c.units,

                cs.capacity,

                COUNT(
                    CASE
                        WHEN e.status = 'enrolled'
                        THEN e.id
                    END
                ) AS enrolled_count,

                (
                    cs.capacity -
                    COUNT(
                        CASE
                            WHEN e.status = 'enrolled'
                            THEN e.id
                        END
                    )
                ) AS remaining_capacity,

                COALESCE(
                    u.full_name,
                    'تخصیص داده نشده'
                ) AS teacher,

                COALESCE(
                    GROUP_CONCAT(
                        sc.day_of_week
                        || ' '
                        || sc.start_time
                        || '-'
                        || sc.end_time,
                        ' | '
                    ),
                    'اعلام نشده'
                ) AS schedule

            FROM course_sections cs

            JOIN courses c
                ON c.id = cs.course_id

            JOIN semesters sem
                ON sem.id = cs.semester_id

            LEFT JOIN professors p
                ON p.id = cs.professor_id

            LEFT JOIN users u
                ON u.id = p.user_id

            LEFT JOIN enrollments e
                ON e.course_section_id = cs.id

            LEFT JOIN schedules sc
                ON sc.course_section_id = cs.id

            WHERE
                sem.status = 'active'
                AND cs.status = 'open'
                AND c.is_active = 1

            GROUP BY cs.id

            ORDER BY c.course_code
            """
        ).fetchall()


def get_course_by_id(course_id: int):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM courses
            WHERE id = ?
            """,
            (course_id,),
        ).fetchone()


def get_course_sections(course_id: int):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                cs.*,
                c.course_code,
                c.course_name,
                c.units,
                COALESCE(
                    u.full_name,
                    'تخصیص داده نشده'
                ) AS teacher
            FROM course_sections cs

            JOIN courses c
                ON c.id = cs.course_id

            LEFT JOIN professors p
                ON p.id = cs.professor_id

            LEFT JOIN users u
                ON u.id = p.user_id

            WHERE cs.course_id = ?

            ORDER BY cs.section_number
            """,
            (course_id,),
        ).fetchall()
def update_course(
    course_id: int,
    course_code: str,
    course_name: str,
    units: int,
    teacher: str,
    capacity: int
):

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE courses
            SET
                course_code=?,
                course_name=?,
                units=?,
                teacher=?,
                capacity=?
            WHERE id=?
            """,
            (
                course_code,
                course_name,
                units,
                teacher,
                capacity,
                course_id
            )
        )

        connection.commit()


    return get_course_by_id(course_id)



def delete_course(course_id: int):

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM courses
            WHERE id=?
            """,
            (course_id,)
        )

        connection.commit()

        return cursor.rowcount > 0