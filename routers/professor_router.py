from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import require_roles
from repositories.university_repository import get_professor_by_user_id

from schemas.professor_schema import ProfessorCreate, ProfessorUpdate

from services.professor_service import (
    create_professor,
    get_professors,
    get_professor_courses,
    get_professor_by_id,
    update_professor,
    delete_professor
)


router = APIRouter(
    prefix="/professors",
    tags=["Professors"]
)



@router.post("/")
def add_professor(
    professor: ProfessorCreate,
    current_user=Depends(require_roles("admin"))
):

    new_professor = create_professor(
        professor.id,
        professor.name,
        professor.department,
        professor.user_id
    )

    return new_professor.to_dict()



@router.get("/")
def list_professors(
    current_user=Depends(require_roles("admin"))
):

    professors = get_professors()

    return [
        professor.to_dict()
        for professor in professors
    ]



@router.get("/{professor_id}")
def get_professor(
    professor_id: int,
    current_user=Depends(require_roles("admin"))
):

    professor = get_professor_by_id(professor_id)

    if professor is None:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return professor.to_dict()



@router.put("/{professor_id}")
def edit_professor(
    professor_id: int,
    professor: ProfessorUpdate,
    current_user=Depends(require_roles("admin"))
):

    updated_professor = update_professor(
        professor_id,
        professor.name,
        professor.department
    )

    if updated_professor is None:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return updated_professor.to_dict()



@router.delete("/{professor_id}")
def remove_professor(
    professor_id: int,
    current_user=Depends(require_roles("admin"))
):

    deleted = delete_professor(professor_id)

    if deleted is False:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    return {
        "message": "Professor deleted successfully"
    }



@router.get("/{professor_id}/courses")
def list_professor_courses(
    professor_id: int,
    current_user=Depends(require_roles("admin", "professor"))
):

    if current_user["role"] == "professor":

        professor = get_professor_by_user_id(
            current_user["id"]
        )

        if professor is None or professor["id"] != professor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )


    courses = get_professor_courses(
        professor_id
    )


    return [
        dict(course)
        for course in courses
    ]