from .objects import *
from ortools.sat.python import cp_model
import yaml # Nested dictionnary pretty print purposes
import time

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
                    
                    # Filter teachers who can teach this subject
                    valid_teachers = [i for i, t in enumerate(self.university.teachers) if subject in t.subjects]

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
                        teacher_var = self.model.NewIntVarFromDomain(
                            cp_model.Domain.FromValues(valid_teachers),
                            f"course_{overall_course_idx}_teacher"
                        )

                        # Create the variable
                        self.variables[group.name][subject.name][overall_course_idx] = {
                            'subject': subject.name, 
                            'group': group.name, 
                            'timeslot': timeslot_var, 
                            'room': room_var, 
                            'teacher': teacher_var
                        }
                    

    def printVariables(self):
        print(yaml.dump(self.variables, allow_unicode=True, default_flow_style=False))


    def createConstraints(self):
        self.noRoomOverlap()
        self.noMultipleCoursesOnTimeslotForGroup()
        self.noTeacherOverlap()
        self.ensureLunchBreak()


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

    
    def noTeacherOverlap(self):
        courses = []
        for _, group in self.variables.items():
            for _, subject in group.items():
                for _, course in subject.items():
                    courses.append(course)

        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                # Create a Boolean variable representing whether two courses have the same timeslot
                same_timeslot = self.model.NewBoolVar(f'same_timeslot_teacher_{i}_{j}')

                self.model.Add(courses[i]['timeslot'] == courses[j]['timeslot']).OnlyEnforceIf(same_timeslot)
                self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot']).OnlyEnforceIf(same_timeslot.Not())

                # Ensure that if timeslots are the same, teachers must be different
                self.model.Add(courses[i]['teacher'] != courses[j]['teacher']).OnlyEnforceIf(same_timeslot)



    def ensureLunchBreak(self):
        # Loop through all courses in the model
        for group_name, subjects in self.variables.items():
            for subject_name, subject_courses in subjects.items():
                for course_idx, course in subject_courses.items():
                    timeslot_var = course['timeslot']
                    
                    # Define the lunch break timeslot indices: index % 7 == 2 (Corresponding to 11:30 -> 13:15)
                    lunch_break_timeslots = [index for index, _ in enumerate(self.university.timeslots) if index % 7 == 2]
                    
                    # Add a constraint that the timeslot should not be any of the lunch break timeslots
                    self.model.Add(timeslot_var != lunch_break_timeslots[0])
                    
                    # Loop through all the lunch break timeslots to enforce no assignment for any of them
                    for lunch_slot in lunch_break_timeslots[1:]:
                        self.model.Add(timeslot_var != lunch_slot)


    def variablesToCourses(self):
        for _, courses in self.variables.items():
            for _, course in courses.items():
                for _, course_details in course.items():
                    
                    # Retrieving the teacher
                    assigned_teacher_index = self.solver.Value(course_details['teacher'])
                    assigned_teacher = self.university.teachers[assigned_teacher_index]
                    
                    # Retrieve the full Subject object based on the subject name
                    subject_name = course_details['subject']
                    subject = None
                    # Assuming 'self.university.subjects' is a dictionary with subject names as keys
                    for promo in self.university.promotions:
                        for sub in promo.subjects:
                            if sub.name == subject_name:
                                subject = sub
                                break
                        if subject:
                            break

                    self.generated_courses.append(
                        Course(self.university.timeslots[self.solver.value(course_details['timeslot'])], 
                        Group(course_details['group']), 
                        subject, 
                        assigned_teacher, 
                        self.university.rooms[self.solver.value(course_details['room'])])
                    )

        #for course in self.generated_courses:
         #   print(course)                 

    def solveCSP(self):
        """Solve the CSP problem."""
        start_time = time.time()

        status = self.solver.Solve(self.model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            print("Solution found:")
            self.variablesToCourses()
            #for _, courses in self.variables.items():
               # for _, course in courses.items():
                #    for _, details in course.items():
                #        #print(f"{details['subject']} | {details['timeslot']}: {self.solver.value(details['timeslot'])} | {details['room']}: {self.solver.value(details['room'])}")            
        else:
            print("No solution found.")

        print(f"Computational time: {round((time.time()-start_time),3)} s")
