from .objects import *
from ortools.sat.python import cp_model
import yaml # Nested dictionnary pretty print purposes

class CSP:
    def __init__(self, university: University):
        self.university = university
        self.model = cp_model.CpModel()
        self.variables = {}  # Dictionary to store variables for each course
        self.generated_courses: List[Course] = []  # List of all generated courses
        self.solver = cp_model.CpSolver()

        self.createVariables()
        #self.printVariables()
        self.createConstraints()
        self.solveCSP()

    def createVariables(self):
        overall_course_idx = 0
        for promo in self.university.promotions:
            for group in promo.groups:
                self.variables[group.name] = {}
                for subject in promo.subjects:
                    self.variables[group.name][subject.name] = {}
                    
                    # Calculate number of timeslots needed for the subject
                    required_hours = subject.hours
                    timeslot_duration = self.university.timeslot_duration  # Assume in hours
                    num_courses = int(required_hours // timeslot_duration)
                    
                    #print("For ", subject.name, " ", num_courses, " courses of", timeslot_duration ," hours are needed.")
                    
                    for idx_course in range(num_courses):
                        overall_course_idx += 1
                        # Timeslot variable
                        timeslot_var = self.model.new_int_var(0, len(self.university.timeslots) - 1, f"course_{overall_course_idx}_timeslot")
                        
                        # Room variable
                        room_var = self.model.new_int_var(0, len(self.university.rooms) - 1, f"course_{overall_course_idx}_room")

                        # Teacher variable
                        teacher_var = self.model.new_int_var(0, len(self.university.teachers) -1, f"course_{overall_course_idx}_teacher")

                        # Create the variable
                        self.variables[group.name][subject.name][overall_course_idx] = {'subject': subject.name, 'group': group.name, 'timeslot': timeslot_var, 'room': room_var, 'teacher': teacher_var}
                    

    def printVariables(self):
        print(yaml.dump(self.variables, allow_unicode=True, default_flow_style=False))


    def createConstraints(self):
        self.noRoomOverlap()
        self.noMultipleCoursesOnTimeslotForGroup()


    def noRoomOverlap(self):
        courses = []
        for _, group in self.variables.items():
            # Group is a Tuple with : (group name, corresponding items)
            for _, subject in group.items():
                # Subject is a Tuple with : (subject name, corresponding items)
                for course_key, course in subject.items():
                    courses.append(course)

        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                # Add constraint: if rooms are the same, timeslots must be different

                # Create a Boolean variable representing the condition
                same_timeslot = self.model.NewBoolVar(f'same_timeslot_{i}_{j}')
                
                # Add the condition to define the Boolean variable
                self.model.Add(courses[i]['timeslot'] == courses[j]['timeslot']).OnlyEnforceIf(same_timeslot)
                self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot']).OnlyEnforceIf(same_timeslot.Not())
                
                # Add the constraint for room overlap, enforced only if the timeslots are the same
                self.model.Add(courses[i]['room'] != courses[j]['room']).OnlyEnforceIf(same_timeslot)

    def noMultipleCoursesOnTimeslotForGroup(self):
        courses = []
        for _, group in self.variables.items():
            # Group is a Tuple with : (group name, corresponding items)
            for _, subject in group.items():
                # Subject is a Tuple with : (subject name, corresponding items)
                for course_key, course in subject.items():
                    courses.append(course)

        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                # Check if the groups are the same
                if courses[i]['group'] == courses[j]['group']:
                    # Add constraint: courses in the same group cannot share the same timeslot
                    self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot'])

        


    def variablesToCourses(self):
        for _, courses in self.variables.items():
            for _, course in courses.items():
                for _, course_details in course.items():
                    self.generated_courses.append(
                        Course(self.university.timeslots[self.solver.value(course_details['timeslot'])], 
                        Group(course_details['group']), 
                        Subject(course_details['subject']), 
                        Teacher("N/A", "N/A"), 
                        self.university.rooms[self.solver.value(course_details['room'])])
                    )

        for course in self.generated_courses:
            print(course)                 

    def solveCSP(self):
        """Solve the CSP problem."""
        
        status = self.solver.Solve(self.model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            print("Solution found:")
            self.variablesToCourses()
            for _, courses in self.variables.items():
                for _, course in courses.items():
                    for _, details in course.items():
                        print(f"{details['subject']} | {details['timeslot']}: {self.solver.value(details['timeslot'])} | {details['room']}: {self.solver.value(details['room'])}")            
        else:
            print("No solution found.")
