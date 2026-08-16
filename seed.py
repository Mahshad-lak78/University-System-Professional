"""Idempotent sample data seed for local development."""

from datetime import datetime, timezone

from core.database import get_connection, initialize_database
from core.security import hash_password


COURSES = [
    ("CE201", "ساختمان داده‌ها", 3),
    ("CE202", "مدار منطقی", 3),
    ("CE203", "معماری کامپیوتر", 3),
    ("CE204", "سیستم عامل", 3),
    ("CE205", "نظریه زبان‌ها و ماشین‌ها", 3),
    ("CE206", "آزمایشگاه مدار منطقی", 1),
]


def seed_demo_data() -> None:
    # Make sure database structure exists
    initialize_database()

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        # =================================================
        # 1. Create / update admin user
        # =================================================

        admin = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = 'admin'
            """
        ).fetchone()

        if admin is None:

            connection.execute(
                """
                INSERT INTO users
                (
                    username,
                    role,
                    full_name,
                    password_hash,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, 'admin', ?, ?, 1, ?, ?)
                """,
                (
                    "admin",
                    "System Administrator",
                    hash_password("admin123"),
                    now,
                    now,
                ),
            )

        else:

            connection.execute(
                """
                UPDATE users
                SET role = 'admin',
                    full_name = ?,
                    is_active = 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    "System Administrator",
                    now,
                    admin["id"],
                ),
            )

        # =================================================
        # 2. Create / update demo professor user
        # =================================================

        professor_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = 'professor'
            """
        ).fetchone()

        if professor_user is None:

            cursor = connection.execute(
                """
                INSERT INTO users
                (
                    username,
                    role,
                    full_name,
                    password_hash,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, 'professor', ?, ?, 1, ?, ?)
                """,
                (
                    "professor",
                    "Demo Professor",
                    hash_password("professor123"),
                    now,
                    now,
                ),
            )

            professor_user_id = cursor.lastrowid

        else:

            professor_user_id = professor_user["id"]

            connection.execute(
                """
                UPDATE users
                SET role = 'professor',
                    full_name = ?,
                    is_active = 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    "Demo Professor",
                    now,
                    professor_user_id,
                ),
            )

        # =================================================
        # 3. Create / update professor
        # =================================================

        professor = connection.execute(
            """
            SELECT id
            FROM professors
            WHERE user_id = ?
            """,
            (professor_user_id,),
        ).fetchone()

        if professor is None:

            cursor = connection.execute(
                """
                INSERT INTO professors
                (
                    user_id,
                    fullname,
                    department,
                    personnel_code,
                    employment_status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'active', ?, ?)
                """,
                (
                    professor_user_id,
                    "Demo Professor",
                    "Computer Engineering",
                    "P-DEMO",
                    now,
                    now,
                ),
            )

            professor_id = cursor.lastrowid

        else:

            professor_id = professor["id"]

            connection.execute(
                """
                UPDATE professors
                SET fullname = ?,
                    department = ?,
                    personnel_code = ?,
                    employment_status = 'active',
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    "Demo Professor",
                    "Computer Engineering",
                    "P-DEMO",
                    now,
                    professor_id,
                ),
            )

        # =================================================
        # 4. Get department
        # =================================================

        department = connection.execute(
            """
            SELECT id
            FROM departments
            WHERE code = 'GENERAL'
            """
        ).fetchone()

        if department is None:

            cursor = connection.execute(
                """
                INSERT INTO departments
                (
                    code,
                    name,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, 1, ?, ?)
                """,
                (
                    "GENERAL",
                    "General Department",
                    now,
                    now,
                ),
            )

            department_id = cursor.lastrowid

        else:

            department_id = department["id"]

        # =================================================
        # 5. Get / create semester
        # =================================================

        semester = connection.execute(
            """
            SELECT id
            FROM semesters
            WHERE code = 'LEGACY-CURRENT'
            """
        ).fetchone()

        if semester is None:

            cursor = connection.execute(
                """
                INSERT INTO semesters
                (
                    code,
                    title,
                    start_date,
                    end_date,
                    registration_start,
                    registration_end,
                    status,
                    max_units_default,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    'active',
                    20,
                    ?,
                    ?
                )
                """,
                (
                    "LEGACY-CURRENT",
                    "Current Semester",
                    "2026-01-01",
                    "2030-12-31",
                    "2026-01-01",
                    "2030-12-31",
                    now,
                    now,
                ),
            )

            semester_id = cursor.lastrowid

        else:

            semester_id = semester["id"]

        # =================================================
        # 6. Get / create classroom
        # =================================================

        classroom = connection.execute(
            """
            SELECT id
            FROM classrooms
            WHERE building = 'Legacy'
              AND room_number = 'ONLINE-1'
            """
        ).fetchone()

        if classroom is None:

            cursor = connection.execute(
                """
                INSERT INTO classrooms
                (
                    building,
                    room_number,
                    capacity,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, 1, ?, ?)
                """,
                (
                    "Legacy",
                    "ONLINE-1",
                    1000,
                    now,
                    now,
                ),
            )

            classroom_id = cursor.lastrowid

        else:

            classroom_id = classroom["id"]

        # =================================================
        # 7. Create / update courses
        # =================================================

        for code, name, units in COURSES:

            course = connection.execute(
                """
                SELECT id
                FROM courses
                WHERE course_code = ?
                """,
                (code,),
            ).fetchone()

            if course is None:

                cursor = connection.execute(
                    """
                    INSERT INTO courses
                    (
                        course_code,
                        course_name,
                        units,
                        teacher,
                        capacity,
                        department_id,
                        is_active,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, 30, ?, 1, ?, ?)
                    """,
                    (
                        code,
                        name,
                        units,
                        "Demo Professor",
                        department_id,
                        now,
                        now,
                    ),
                )

                course_id = cursor.lastrowid

            else:

                course_id = course["id"]

                connection.execute(
                    """
                    UPDATE courses
                    SET course_name = ?,
                        units = ?,
                        teacher = ?,
                        department_id = ?,
                        is_active = 1,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        name,
                        units,
                        "Demo Professor",
                        department_id,
                        now,
                        course_id,
                    ),
                )

            # =================================================
            # 8. Create / update course section
            # =================================================

            section = connection.execute(
                """
                SELECT id
                FROM course_sections
                WHERE course_id = ?
                  AND semester_id = ?
                  AND section_number = '01'
                """,
                (
                    course_id,
                    semester_id,
                ),
            ).fetchone()

            if section is None:

                connection.execute(
                    """
                    INSERT INTO course_sections
                    (
                        course_id,
                        semester_id,
                        professor_id,
                        classroom_id,
                        section_number,
                        capacity,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, '01', 30, 'open', ?, ?)
                    """,
                    (
                        course_id,
                        semester_id,
                        professor_id,
                        classroom_id,
                        now,
                        now,
                    ),
                )

            else:

                connection.execute(
                    """
                    UPDATE course_sections
                    SET professor_id = ?,
                        classroom_id = ?,
                        capacity = 30,
                        status = 'open',
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        professor_id,
                        classroom_id,
                        now,
                        section["id"],
                    ),
                )

        # =================================================
        # 9. Make sure all existing sections have professor
        # =================================================

        connection.execute(
            """
            UPDATE course_sections
            SET professor_id = ?,
                updated_at = ?
            WHERE professor_id IS NULL
            """,
            (
                professor_id,
                now,
            ),
        )

    print("Demo data seeded successfully.")


if __name__ == "__main__":
    seed_demo_data()
