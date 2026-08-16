from models.academic import StudentProfile, User
from models.entities import CourseSection, EnrollmentDecision


student = StudentProfile(1, 11, "S140500001", 1, "Computer Engineering", "active")
user = User(11, "student", "Student Name", "student", True)
section = CourseSection(5, 2, 1, 30, "open")
enrollment = EnrollmentDecision(9, student.id, section.id)

assert user.role == "student"
assert enrollment.course_section_id == 5
print("model smoke test passed")
