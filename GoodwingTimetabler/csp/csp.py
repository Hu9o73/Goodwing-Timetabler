from .objects import *
from ortools.sat.python import cp_model


class CSP:
    def __init__(self, university: University):
        self.university = university
        self.model = cp_model.CpModel()
        self.variables = {}  # Dictionary to store variables for each course
        self.generated_courses = []  # List of all generated courses
        self.solver = cp_model.CpSolver()

        # Dynamically create courses
        self.createCourses()

        # Create variables for CSP
        self.createVariables()

        # Add constraints
        self.setupConstraints()

        # Solve the CSP
        self.solveCSP()

    def createCourses(self):
        """Generate courses based on subjects, groups, and required hours."""
        for promotion in self.university.promotions:
            for group in promotion.groups:
                for subject in promotion.subjects:
                    # Calculate number of timeslots needed for the subject
                    required_hours = subject.hours
                    timeslot_duration = self.university.timeslot_duration  # Assume in hours
                    num_courses = int(required_hours // timeslot_duration)

                    for _ in range(num_courses):
                        # Assign a qualified teacher for the subject
                        qualified_teachers = [teacher for teacher in self.university.teachers if subject in teacher.subjects]
                        if not qualified_teachers:
                            raise ValueError(f"No qualified teacher found for subject {subject.name}")
                        
                        teacher = qualified_teachers[0]  # Pick the first qualified teacher (you could add logic to rotate)
                        room = self.university.rooms[0]  # Default room assignment for now (CSP will handle conflicts)
                        timeslot = self.university.timeslots[0] # Default timeslot is the first one

                        # Create the course
                        course = Course(timeslot, group, subject, teacher, room)
                        self.generated_courses.append(course)

    def createVariables(self):
        """Create variables for timeslot and room assignments."""
        for idx, course in enumerate(self.generated_courses):
            # Timeslot variables
            timeslot_var = self.model.new_int_var(0, len(self.university.timeslots) - 1, f"course_{idx}_timeslot")
            
            # Room variables
            room_var = self.model.new_int_var(0, len(self.university.rooms) - 1, f"course_{idx}_room")

            # Save these variables
            self.variables[course] = {'timeslot': timeslot_var, 'room': room_var}

    def setupConstraints(self):
        """Add constraints to the model."""
        # Constraint 1: No room overlap
        self.noRoomOverlap()

        # Constraint 2: No teacher duplication
        #self.noDuplicateTeacher()

        # Constraint 3: No group duplication
        #self.noDuplicateGroup()

        # Constraint 4: Teacher assigned only to their subjects
        #self.teachersAssignedToTheirSubject()

    def noRoomOverlap(self):
        """No two courses can occupy the same room at the same timeslot."""
        for timeslot_idx in range(len(self.university.timeslots)):
            for room_idx in range(len(self.university.rooms)):
                
                # Create a sum for courses assigned to this room and timeslot
                courses_in_room = []

                for course in self.generated_courses:
                    # Create a helper variable indicating if the course is in this room
                    is_in_room = self.model.NewBoolVar(f"{course}_in_room_{room_idx}_timeslot_{timeslot_idx}")
                    
                    # Add a constraint linking the helper variable to the room assignment
                    self.model.Add(self.variables[course]['room'] == room_idx).OnlyEnforceIf(is_in_room)
                    self.model.Add(self.variables[course]['room'] != room_idx).OnlyEnforceIf(is_in_room.Not())

                    courses_in_room.append(is_in_room)

                # Add a constraint to ensure at most one course is assigned to this room at this timeslot
                self.model.Add(sum(courses_in_room) <= 1)


    def noDuplicateTeacher(self):
        """A teacher cannot teach multiple courses at the same timeslot."""
        for timeslot_idx in range(len(self.university.timeslots)):
            for teacher in self.university.teachers:
                # Collect courses taught by the same teacher at the same timeslot
                courses_by_teacher = [
                    (self.variables[course]['timeslot'] == timeslot_idx)
                    for course in self.generated_courses if course.teacher == teacher
                ]
                # At most one course per teacher per timeslot
                self.model.add(sum(courses_by_teacher) <= 1)

    def noDuplicateGroup(self):
        """A group cannot attend multiple courses at the same timeslot."""
        for timeslot_idx in range(len(self.university.timeslots)):
            for group in [course.group for course in self.generated_courses]:
                # Collect courses attended by the same group at the same timeslot
                courses_for_group = [
                    (self.variables[course]['timeslot'] == timeslot_idx)
                    for course in self.generated_courses if course.group == group
                ]
                print("On timeslot ", timeslot_idx, ", for group ", group, " overlapping courses: ", sum(courses_for_group))
                print("T/F : ", sum(courses_for_group) <= 1)
                # At most one course per group per timeslot
                self.model.add(sum(courses_for_group) <= 1)

    def teachersAssignedToTheirSubject(self):
        """Teachers can only teach subjects they are qualified for."""
        for course in self.generated_courses:
            # Add constraint that the teacher must be qualified
            if course.subject not in course.teacher.subjects:
                self.model.add(False)  # Invalid assignment for this course

    def solveCSP(self):
        """Solve the CSP problem."""
        
        status = self.solver.Solve(self.model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            print("Solution found:")
            for course, vars in self.variables.items():
                timeslot = self.solver.Value(vars['timeslot'])
                room_idx = self.solver.Value(vars['room'])
                room = self.university.rooms[room_idx]
                print(f"Course: {course.subject.name}, Group: {course.group.name}, Teacher: {course.teacher.name}, Timeslot: {timeslot}, Room: {room.name}")
        else:
            print("No solution found.")
