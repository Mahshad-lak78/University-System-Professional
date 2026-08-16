from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool


@dataclass(frozen=True)
class StudentProfile:
    id: int
    user_id: int
    student_number: str
    department_id: int
    major: str
    academic_status: str


@dataclass(frozen=True)
class GradeRecord:
    enrollment_id: int
    score: float | None
    status: str
    graded_by_professor_id: int | None
