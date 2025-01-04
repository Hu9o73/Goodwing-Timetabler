from .objects import *

class CSP:
    """
    Object representing an instance of our CSP problem.\n
    Parameters:\n
    - univeristy : University | Our university, with its promotions, groups, teachers, etc...
    - courses : [Course] | The list of scheduled courses
    \n
    This class is made to verify that the given list of courses satisfies the constraints of the university.
    """
    def __init__(self, university: University, courses: List[Course]):
        self.university = university
        self.courses = courses