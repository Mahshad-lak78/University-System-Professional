from models.professor import Professor
from database_connection import get_connection


professors = []



def create_professor(id, name, department, user_id=None):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO professors(
            fullname,
            department,
            user_id
        )
        VALUES (?, ?, ?)
        """,
        (
            name,
            department,
            user_id
        )
    )


    connection.commit()


    new_id = cursor.lastrowid


    connection.close()


    professor = Professor(
        new_id,
        name,
        department
    )


    return professor





def get_professors():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM professors
        """
    )


    rows = cursor.fetchall()


    connection.close()


    professor_list = []


    for row in rows:

        professor = Professor(
            row["id"],
            row["fullname"],
            row["department"]
        )

        professor_list.append(professor)


    return professor_list





def get_professor_courses(professor_id):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM courses
        WHERE professor_id=?
        """,
        (professor_id,)
    )


    courses = cursor.fetchall()


    connection.close()


    return courses





def assign_course_to_professor(professor, course):

    professor.add_course(course)

    course.assign_professor(professor)

    return professor





def remove_course_from_professor(professor, course):

    professor.remove_course(course)

    return professor
def get_professor_by_id(professor_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM professors
        WHERE id=?
        """,
        (professor_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    professor = Professor(
        row["id"],
        row["fullname"],
        row["department"]
    )

    return professor



def update_professor(professor_id, name, department):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE professors
        SET fullname=?, department=?
        WHERE id=?
        """,
        (
            name,
            department,
            professor_id
        )
    )

    connection.commit()

    connection.close()

    return get_professor_by_id(professor_id)



def delete_professor(professor_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM professors
        WHERE id=?
        """,
        (professor_id,)
    )

    connection.commit()

    connection.close()

    return True