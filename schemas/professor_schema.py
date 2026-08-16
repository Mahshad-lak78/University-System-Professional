from pydantic import BaseModel


class ProfessorCreate(BaseModel):

    id: int
    name: str
    department: str
    user_id: int



class ProfessorUpdate(BaseModel):

    name: str
    department: str