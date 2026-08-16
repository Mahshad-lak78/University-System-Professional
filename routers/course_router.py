from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_roles

from schemas.course_schema import CourseCreate, CourseUpdate

from services.course_service import (
    create_course,
    get_courses,
    get_course_by_id,
    update_course,
    delete_course
)


router = APIRouter(
    prefix="/api/courses",
    tags=["Courses"]
)



@router.post("/", status_code=201)
def add_course(
    course: CourseCreate,
    current_user=Depends(require_roles("admin"))
):

    return dict(
        create_course(
            course.course_code,
            course.course_name,
            course.units,
            course.teacher,
            course.capacity
        )
    )



@router.get("/")
def list_courses():

    return [
        dict(course)
        for course in get_courses()
    ]



@router.get("/{course_id}")
def get_course(
    course_id: int
):

    course = get_course_by_id(course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return dict(course)



@router.put("/{course_id}")
def edit_course(
    course_id: int,
    course: CourseUpdate,
    current_user=Depends(require_roles("admin"))
):

    updated_course = update_course(
        course_id,
        course.course_code,
        course.course_name,
        course.units,
        course.teacher,
        course.capacity
    )

    if updated_course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return dict(updated_course)



@router.delete("/{course_id}")
def remove_course(
    course_id: int,
    current_user=Depends(require_roles("admin"))
):

    deleted = delete_course(course_id)

    if deleted is False:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }