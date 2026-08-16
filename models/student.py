from models.person import Person


class Student(Person):

    def __init__(self, id, name, major):
        super().__init__(id, name)

        self.major = major
        self.courses = []


    def add_course(self, course):
        self.courses.append(course)


    def drop_course(self, course):
        if course in self.courses:
            self.courses.remove(course)


    def to_dict(self):
        data = super().to_dict()

        data.update({
            "major": self.major,
            "courses": [
                course.to_dict()
                for course in self.courses
            ]
        })

        return data