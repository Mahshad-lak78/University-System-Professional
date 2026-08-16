import sqlite3
import tempfile
import unittest
from pathlib import Path

from migrations.migrate_v2 import run_migrations


class MigrationTests(unittest.TestCase):
    def test_legacy_students_courses_and_enrollments_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "university.db"
            connection = sqlite3.connect(path)
            connection.executescript(
                """CREATE TABLE students (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, fullname TEXT);
                   CREATE TABLE courses (id INTEGER PRIMARY KEY, course_code TEXT, course_name TEXT, units INTEGER, teacher TEXT, capacity INTEGER);
                   CREATE TABLE enrollments (id INTEGER PRIMARY KEY, student_id INTEGER, course_id INTEGER);
                   INSERT INTO students VALUES (7, 'legacy_student', 'legacy-pass', 'Legacy Student');
                   INSERT INTO courses VALUES (9, 'CE999', 'Legacy Course', 3, 'Legacy Teacher', 19);
                   INSERT INTO enrollments VALUES (11, 7, 9);"""
            )
            connection.commit()
            connection.close()
            run_migrations(path)
            connection = sqlite3.connect(path)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM students WHERE id = 7").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM courses WHERE id = 9").fetchone()[0], 1)
            enrollment = connection.execute("SELECT course_section_id, registered_units, status FROM enrollments WHERE id = 11").fetchone()
            self.assertIsNotNone(enrollment[0])
            self.assertEqual(enrollment[1], 3)
            self.assertEqual(enrollment[2], "enrolled")
            self.assertTrue((path.parent / "backups" / "university-pre-ums-v2.db").exists())
            connection.close()


if __name__ == "__main__":
    unittest.main()
