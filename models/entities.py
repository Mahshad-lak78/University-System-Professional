from dataclasses import dataclass


@dataclass(frozen=True)
class CourseSection:
    id: int
    course_id: int
    semester_id: int
    capacity: int
    status: str


@dataclass(frozen=True)
class EnrollmentDecision:
    enrollment_id: int
    student_id: int
    course_section_id: int
