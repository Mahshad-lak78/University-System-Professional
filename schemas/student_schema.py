from pydantic import BaseModel


class StudentCreate(BaseModel):

    id: int
    name: str
    major: str
    user_id: int



class StudentUpdate(BaseModel):

    name: str
    major: str