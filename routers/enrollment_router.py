from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_current_user, require_roles

from repositories.university_repository import get_student_by_user_id

from services.enrollment_service_v2 import (
    EnrollmentError,
    enroll_authenticated_student,
    get_enrollments_for_student,
    drop_authenticated_student
)

from schemas.ums_schema import EnrollmentCreate


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


@router.post("/", status_code=201)
def add_enrollment(
    data: EnrollmentCreate,
    current_user=Depends(require_roles("student"))
):

    try:

        enrollment_id = enroll_authenticated_student(
            current_user["id"],
            data.course_section_id
        )

    except EnrollmentError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc


    return {
        "id": enrollment_id,
        "message": "Enrollment created"
    }





@router.get("/me")
def my_enrollments(
    current_user=Depends(require_roles("student"))
):

    student = get_student_by_user_id(
        current_user["id"]
    )


    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    return [
        dict(row)
        for row in get_enrollments_for_student(student["id"])
    ]





@router.get("/{student_id}")
def student_courses(
    student_id: int,
    current_user=Depends(get_current_user)
):

    if current_user["role"] == "student":

        student = get_student_by_user_id(
            current_user["id"]
        )

        if student is None or student["id"] != student_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )


    elif current_user["role"] != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )


    return [
        dict(row)
        for row in get_enrollments_for_student(student_id)
    ]





@router.delete("/{course_section_id}")
def drop_course(
    course_section_id: int,
    current_user=Depends(require_roles("student"))
):

    try:

        drop_authenticated_student(
            current_user["id"],
            course_section_id
        )


    except EnrollmentError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc


    return {
        "message": "Course dropped successfully",
        "course_section_id": course_section_id
    }