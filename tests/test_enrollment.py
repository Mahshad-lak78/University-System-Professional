import unittest

from core.database import get_connection
from services.enrollment_service_v2 import EnrollmentError, enroll_authenticated_student
from services.grade_service import upsert_grade
from tests.helpers import seed_professor, seed_section, seed_student, temporary_database


class EnrollmentTests(unittest.TestCase):
    def test_enrollment_and_duplicate_protection(self):
        with temporary_database():
            user_id, _ = seed_student()
            _, section_id = seed_section()
            enrollment_id = enroll_authenticated_student(user_id, section_id)
            self.assertGreater(enrollment_id, 0)
            with self.assertRaisesRegex(EnrollmentError, "already enrolled"):
                enroll_authenticated_student(user_id, section_id)

    def test_capacity_is_enforced(self):
        with temporary_database():
            first_user, _ = seed_student("first")
            second_user, _ = seed_student("second")
            _, section_id = seed_section(capacity=1)
            enroll_authenticated_student(first_user, section_id)
            with self.assertRaisesRegex(EnrollmentError, "full"):
                enroll_authenticated_student(second_user, section_id)

    def test_prerequisite_is_enforced(self):
        with temporary_database():
            user_id, _ = seed_student()
            prerequisite_course, _ = seed_section("CE100")
            course_id, section_id = seed_section("CE200")
            with get_connection() as connection:
                connection.execute("INSERT INTO course_prerequisites (course_id, prerequisite_course_id, minimum_score, created_at) VALUES (?, ?, 10, '2026-01-01')", (course_id, prerequisite_course))
            with self.assertRaisesRegex(EnrollmentError, "Prerequisite"):
                enroll_authenticated_student(user_id, section_id)

    def test_schedule_conflict_is_enforced(self):
        with temporary_database():
            user_id, _ = seed_student()
            _, current_section = seed_section("CE100")
            _, conflicting_section = seed_section("CE200")
            with get_connection() as connection:
                connection.execute("INSERT INTO schedules (course_section_id, day_of_week, start_time, end_time, created_at, updated_at) VALUES (?, 1, '09:00', '11:00', 'x', 'x')", (current_section,))
                connection.execute("INSERT INTO schedules (course_section_id, day_of_week, start_time, end_time, created_at, updated_at) VALUES (?, 1, '10:00', '12:00', 'x', 'x')", (conflicting_section,))
            enroll_authenticated_student(user_id, current_section)
            with self.assertRaisesRegex(EnrollmentError, "Schedule conflict"):
                enroll_authenticated_student(user_id, conflicting_section)

    def test_maximum_units_is_enforced(self):
        with temporary_database():
            user_id, _ = seed_student()
            _, first_section = seed_section("CE100", units=3)
            _, second_section = seed_section("CE200", units=1)
            with get_connection() as connection:
                connection.execute("UPDATE semesters SET max_units_default = 3 WHERE status = 'active'")
            enroll_authenticated_student(user_id, first_section)
            with self.assertRaisesRegex(EnrollmentError, "Maximum allowed units"):
                enroll_authenticated_student(user_id, second_section)

    def test_student_status_active_semester_active_course_and_section_are_enforced(self):
        with temporary_database():
            suspended_user, _ = seed_student(status="suspended")
            course_id, section_id = seed_section()
            with self.assertRaisesRegex(EnrollmentError, "not eligible"):
                enroll_authenticated_student(suspended_user, section_id)

            active_user, _ = seed_student("active")
            with get_connection() as connection:
                connection.execute("UPDATE semesters SET status = 'closed' WHERE status = 'active'")
            with self.assertRaisesRegex(EnrollmentError, "Semester is not active"):
                enroll_authenticated_student(active_user, section_id)

        with temporary_database():
            user_id, _ = seed_student()
            course_id, section_id = seed_section()
            with get_connection() as connection:
                connection.execute("UPDATE courses SET is_active = 0 WHERE id = ?", (course_id,))
            with self.assertRaisesRegex(EnrollmentError, "not available"):
                enroll_authenticated_student(user_id, section_id)

    def test_professor_can_publish_grade_only_for_own_section(self):
        with temporary_database():
            student_user, _ = seed_student()
            professor_user, professor_id = seed_professor()
            _, section_id = seed_section(professor_id=professor_id)
            enrollment_id = enroll_authenticated_student(student_user, section_id)
            grade_id = upsert_grade(professor_user, enrollment_id, 18.5, True)
            self.assertGreater(grade_id, 0)
            with get_connection() as connection:
                grade = connection.execute("SELECT score, status FROM grades WHERE id = ?", (grade_id,)).fetchone()
            self.assertEqual(grade["score"], 18.5)
            self.assertEqual(grade["status"], "published")


if __name__ == "__main__":
    unittest.main()
