from datetime import date, time

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=120)


class CourseCreateV2(BaseModel):
    department_id: int
    course_code: str = Field(min_length=2, max_length=20)
    course_name: str = Field(min_length=2, max_length=120)
    units: int = Field(ge=1, le=5)
    description: str | None = Field(default=None, max_length=1000)


class EnrollmentCreate(BaseModel):
    course_section_id: int


class GradeUpsert(BaseModel):
    score: float = Field(ge=0, le=20)
    publish: bool = False


class ScheduleCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
