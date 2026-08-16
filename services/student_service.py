from models.student import Student
from database_connection import get_connection


students = []



def create_student(id, name, major, user_id=None):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO students(
            fullname,
            username,
            password,
            user_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            name,
            "123456",
            user_id
        )
    )


    connection.commit()


    new_id = cursor.lastrowid


    connection.close()


    student = Student(
        new_id,
        name,
        major
    )


    return student





def get_students():

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM students
        """
    )


    rows = cursor.fetchall()


    connection.close()


    student_list = []


    for row in rows:

        student = Student(
            row["id"],
            row["fullname"],
            "Computer Engineering"
        )

        student_list.append(student)


    return student_list





def get_student_by_id(student_id):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )


    row = cursor.fetchone()


    connection.close()


    if row is None:
        return None


    student = Student(
        row["id"],
        row["fullname"],
        "Computer Engineering"
    )


    return student





def update_student(student_id, name, major):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE students
        SET fullname = ?
        WHERE id = ?
        """,
        (
            name,
            student_id
        )
    )


    connection.commit()


    updated = cursor.rowcount > 0


    connection.close()


    if not updated:
        return None


    return get_student_by_id(student_id)





def delete_student(student_id):

    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(
        """
        DELETE FROM students
        WHERE id = ?
        """,
        (student_id,)
    )


    connection.commit()


    deleted = cursor.rowcount > 0


    connection.close()


    return deleted





def add_course_to_student(student, course):

    student.add_course(course)

    return student





def remove_course_from_student(student, course):

    student.drop_course(course)

    return student