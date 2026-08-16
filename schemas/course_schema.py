from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    units: int = Field(gt=0)
    teacher: str
    capacity: int = Field(ge=0)



class CourseUpdate(BaseModel):
    course_code: str
    course_name: str
    units: int = Field(gt=0)
    teacher: str
    capacity: int = Field(ge=0)
