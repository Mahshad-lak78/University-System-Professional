from schemas.ums_schema import CourseCreateV2, DepartmentCreate, EnrollmentCreate, GradeUpsert


department = DepartmentCreate(code="CE", name="Computer Engineering")
course = CourseCreateV2(department_id=1, course_code="CE101", course_name="Programming", units=3)
enrollment = EnrollmentCreate(course_section_id=2)
grade = GradeUpsert(score=18.5, publish=True)

assert department.code == "CE"
assert course.units == 3
assert enrollment.course_section_id == 2
assert grade.publish is True
print("schema smoke test passed")
