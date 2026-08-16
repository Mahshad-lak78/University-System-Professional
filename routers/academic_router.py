from fastapi import APIRouter, Depends, HTTPException

from core.dependencies import require_roles
from repositories.academic_repository import dashboard_counts, list_current_sections, list_departments, student_enrollments
from schemas.ums_schema import CourseCreateV2, DepartmentCreate, EnrollmentCreate, GradeUpsert
from services.academic_service import AcademicError, create_course, create_department
from services.enrollment_service_v2 import EnrollmentError, drop_authenticated_student, enroll_authenticated_student
from services.grade_service import GradeError, upsert_grade


router = APIRouter(prefix="/api/v1", tags=["University Management"])


@router.get("/departments")
def get_departments():
    return [dict(row) for row in list_departments()]


@router.post("/departments", status_code=201)
def add_department(data: DepartmentCreate, current_user=Depends(require_roles("admin"))):
    try:
        return {"id": create_department(data.code, data.name)}
    except AcademicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sections")
def get_sections(current_user=Depends(require_roles("admin", "professor", "student"))):
    return [dict(row) for row in list_current_sections()]


@router.post("/courses", status_code=201)
def add_course(data: CourseCreateV2, current_user=Depends(require_roles("admin"))):
    try:
        return {"id": create_course(data.department_id, data.course_code, data.course_name, data.units, data.description)}
    except AcademicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/enrollments/me")
def my_enrollments(current_user=Depends(require_roles("student"))):
    return [dict(row) for row in student_enrollments(current_user["id"])]


@router.post("/enrollments", status_code=201)
def enroll(data: EnrollmentCreate, current_user=Depends(require_roles("student"))):
    try:
        return {"id": enroll_authenticated_student(current_user["id"], data.course_section_id)}
    except EnrollmentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/enrollments/{course_section_id}", status_code=204)
def drop(course_section_id: int, current_user=Depends(require_roles("student"))):
    try:
        drop_authenticated_student(current_user["id"], course_section_id)
    except EnrollmentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/grades/{enrollment_id}")
def save_grade(enrollment_id: int, data: GradeUpsert, current_user=Depends(require_roles("professor"))):
    try:
        return {"id": upsert_grade(current_user["id"], enrollment_id, data.score, data.publish)}
    except GradeError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/admin/dashboard")
def admin_dashboard(current_user=Depends(require_roles("admin"))):
    return dashboard_counts()
