class Course:


    def __init__(
        self,
        id,
        course_code,
        name,
        units,
        teacher,
        capacity
    ):

        self.id = id

        self.course_code = course_code

        self.name = name

        self.units = units

        self.teacher = teacher

        self.capacity = capacity



    def to_dict(self):

        return {

            "id": self.id,

            "course_code": self.course_code,

            "name": self.name,

            "units": self.units,

            "teacher": self.teacher,

            "capacity": self.capacity

        }