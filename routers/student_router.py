from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_roles

from schemas.student_schema import StudentCreate, StudentUpdate

from services.student_service import (
    create_student,
    get_students,
    get_student_by_id,
    update_student,
    delete_student
)


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.post("/")
def add_student(
    student: StudentCreate,
    current_user=Depends(require_roles("admin"))
):

    new_student = create_student(
        student.id,
        student.name,
        student.major,
        student.user_id
    )

    return new_student.to_dict()


@router.get("/")
def list_students(
    current_user=Depends(require_roles("admin"))
):

    students = get_students()

    return [
        student.to_dict()
        for student in students
    ]


@router.get("/{student_id}")
def get_student(
    student_id: int,
    current_user=Depends(require_roles("admin"))
):

    student = get_student_by_id(student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student.to_dict()


@router.put("/{student_id}")
def edit_student(
    student_id: int,
    student: StudentUpdate,
    current_user=Depends(require_roles("admin"))
):

    updated_student = update_student(
        student_id,
        student.name,
        student.major
    )

    if updated_student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return updated_student.to_dict()


@router.delete("/{student_id}")
def remove_student(
    student_id: int,
    current_user=Depends(require_roles("admin"))
):

    deleted = delete_student(student_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }