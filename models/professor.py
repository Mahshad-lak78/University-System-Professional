from models.person import Person


class Professor(Person):

    def __init__(self, id, name, department):
        super().__init__(id, name)

        self.department = department
        self.courses = []


    def add_course(self, course):
        self.courses.append(course)


    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)


    def to_dict(self):
        data = super().to_dict()

        data.update({
            "department": self.department,
            "courses": [
                course.to_dict()
                for course in self.courses
            ]
        })

        return data