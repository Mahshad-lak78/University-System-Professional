from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

from routers import auth_router
from routers import course_router
from routers import enrollment_router
from routers import professor_router
from routers import student_router
from routers import academic_router

from core.database import initialize_database
from core.security import session_secret

from repositories.university_repository import (
    get_student_by_user_id,
    get_user_by_id
)

from services.course_service import get_available_sections

from services.dashboard_service import (
    get_student_dashboard
)

from services.enrollment_service_v2 import (
    EnrollmentError,
    drop_authenticated_student,
    enroll_authenticated_student
)


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):

    initialize_database()

    yield



app = FastAPI(
    title="University System",
    version="3.0",
    lifespan=lifespan,
)


# Session support
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret
)



app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)



templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)



app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(professor_router.router)
app.include_router(course_router.router)
app.include_router(enrollment_router.router)
app.include_router(academic_router.router)




def current_student(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return None


    user = get_user_by_id(user_id)


    if (
        user is None
        or user["role"] != "student"
        or not user["is_active"]
    ):
        return None


    return get_student_by_user_id(user_id)





def login_required(request: Request):

    student = current_student(request)


    if student is None:

        return RedirectResponse(
            url="/",
            status_code=303
        )


    return student





@app.get("/", include_in_schema=False)
def home(request: Request):

    if current_student(request):

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )


    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )





@app.get("/register", include_in_schema=False)
def register_page(request: Request):

    if current_student(request):

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )


    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )





@app.get("/dashboard", include_in_schema=False)
def dashboard(request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    dashboard_data = get_student_dashboard(
        student["user_id"]
    )


    if dashboard_data is None:

        return RedirectResponse(
            url="/",
            status_code=303
        )



    student_info, courses = dashboard_data



    total_units = sum(
        course["units"]
        for course in courses
    )



    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={

            "fullname": student_info["full_name"],

            "student": student_info,

            "courses": courses,

            "course_count": len(courses),

            "total_units": total_units

        }
    )





@app.get("/courses", include_in_schema=False)
def courses_page(request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    return templates.TemplateResponse(

        request=request,

        name="courses.html",

        context={

            "courses": get_available_sections(),

            "message": request.query_params.get("message")

        }
    )





@app.post("/enroll/{course_id}", include_in_schema=False)
def enroll_page(course_id: int, request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    try:

        enroll_authenticated_student(
            student["user_id"],
            course_id
        )

        message = "انتخاب واحد با موفقیت انجام شد."


    except EnrollmentError as exc:

        message = str(exc)



    return RedirectResponse(

        url=f"/courses?message={message}",

        status_code=303

    )





@app.get("/my-courses", include_in_schema=False)
def my_courses_page(request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    _, courses = get_student_dashboard(
        student["user_id"]
    )



    return templates.TemplateResponse(

        request=request,

        name="my_courses.html",

        context={

            "courses": courses,

            "message": request.query_params.get("message")

        }
    )





@app.post("/drop/{course_id}", include_in_schema=False)
def drop_course_page(course_id: int, request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    try:

        drop_authenticated_student(
            student["user_id"],
            course_id
        )

        message = "درس با موفقیت حذف شد."


    except EnrollmentError as exc:

        message = str(exc)



    return RedirectResponse(

        url=f"/my-courses?message={message}",

        status_code=303

    )





@app.get("/profile", include_in_schema=False)
def profile_page(request: Request):

    student = login_required(request)


    if isinstance(student, RedirectResponse):

        return student



    return templates.TemplateResponse(

        request=request,

        name="profile.html",

        context={

            "student": student

        }
    )





@app.get("/health")
def health():

    return {

        "status": "ok"

    }





@app.get("/api")
def api_home():

    return {

        "message": "University System API is running"

    }