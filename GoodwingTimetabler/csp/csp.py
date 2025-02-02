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

        # Store objective terms
        self.gap_penalties = []  # For storing gap penalties
        self.balance_penalties = []  # For storing balance penalties

        self.createVariables()
        #self.printVariables()
        self.createConstraints()
        self.createSoftConstraints()
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
        self.teacherAvailabilityConstraint()
        self.ensureLunchBreak()
        self.restrictWeekendTimeslots()

    def createSoftConstraints(self):
        self.balanceCoursesAcrossDays()  # Let's start with just this one
        
        # Use a smaller weight for the balance penalties
        if self.balance_penalties:
            total_cost = sum(self.balance_penalties)
            self.model.Minimize(total_cost)
            
            # Debug
            #print(f"Added {len(self.balance_penalties)} balance penalties to objective")

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

    def teacherAvailabilityConstraint(self):
        """
        Ensures teachers are only assigned to courses during their available timeslots.
        """
        courses = []
        for _, group in self.variables.items():
            for _, subject in group.items():
                for _, course in subject.items():
                    courses.append(course)

        for course in courses:
            teacher_var = course['teacher']
            timeslot_var = course['timeslot']
            
            # For each potential teacher
            for teacher_idx, teacher in enumerate(self.university.teachers):
                if hasattr(teacher, 'available_slots') and teacher.available_slots:
                    # Create a boolean variable for when this teacher is selected
                    is_selected = self.model.NewBoolVar(f'teacher_{teacher_idx}_available_for_{id(course)}')
                    
                    # Link the boolean to the teacher assignment
                    self.model.Add(teacher_var == teacher_idx).OnlyEnforceIf(is_selected)
                    self.model.Add(teacher_var != teacher_idx).OnlyEnforceIf(is_selected.Not())
                    
                    # Create a boolean variable for each available timeslot
                    timeslot_bools = []
                    for ts_idx in teacher.available_slots:
                        is_timeslot = self.model.NewBoolVar(f'is_timeslot_{ts_idx}_for_{id(course)}')
                        self.model.Add(timeslot_var == ts_idx).OnlyEnforceIf(is_timeslot)
                        self.model.Add(timeslot_var != ts_idx).OnlyEnforceIf(is_timeslot.Not())
                        timeslot_bools.append(is_timeslot)
                    
                    # If this teacher is selected, the timeslot MUST be one of their available slots
                    self.model.AddBoolOr(timeslot_bools).OnlyEnforceIf(is_selected)

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

    def restrictWeekendTimeslots(self):
        """
        Ensures no courses are scheduled:
        - After the 3rd timeslot on Saturday (timeslots 3-6 of day 5)
        - All day Sunday (timeslots 0-6 of day 6)
        """
        # Get all courses from all groups
        all_courses = []
        for group_courses in self.variables.values():
            for subject_courses in group_courses.values():
                all_courses.extend(subject_courses.values())
        
        # For each course, add constraints for weekend restrictions
        for course in all_courses:
            timeslot_var = course['timeslot']
            
            # Calculate forbidden timeslots
            # Saturday afternoon (day 5, timeslots 3-6)
            saturday_forbidden = list(range(5 * 7 + 3, 5 * 7 + 7))  # Timeslots 38-41
            # All Sunday (day 6, timeslots 0-6)
            sunday_forbidden = list(range(6 * 7, 6 * 7 + 7))    # Timeslots 42-48
            
            # Combine all forbidden timeslots
            forbidden_timeslots = saturday_forbidden + sunday_forbidden
            
            # Add constraint to prevent scheduling in these timeslots
            for forbidden_ts in forbidden_timeslots:
                self.model.Add(timeslot_var != forbidden_ts)

    def balanceCoursesAcrossDays(self):
        # Process each group separately
        for group_name, subjects in self.variables.items():
            # Debug
            #print(f"\nProcessing group: {group_name}")
            
            # Get all courses for this group
            group_courses = []
            for subject_courses in subjects.values():
                group_courses.extend(subject_courses.values())
            
            # Debug
            #print(f"Found {len(group_courses)} courses for this group")
            
            num_days = len(self.university.timeslots) // 7
            total_courses = len(group_courses)
            target_courses_per_day = total_courses / num_days
            
            # Debug
            #print(f"Target courses per day: {target_courses_per_day}")
            
            # Count courses per day
            day_counts = []
            for day in range(num_days):
                # Create course counters for this day
                day_courses = self.model.NewIntVar(0, len(group_courses), f'day_count_{group_name}_{day}')
                day_start = day * 7
                day_end = day_start + 7
                
                # Count how many courses are on this day
                course_indicators = []
                for course in group_courses:
                    is_on_day = self.model.NewBoolVar(f'course_on_day_{group_name}_{day}_{id(course)}')
                    self.model.Add(course['timeslot'] >= day_start).OnlyEnforceIf(is_on_day)
                    self.model.Add(course['timeslot'] < day_end).OnlyEnforceIf(is_on_day)
                    course_indicators.append(is_on_day)
                
                self.model.Add(day_courses == sum(course_indicators))
                day_counts.append(day_courses)
            
            # Add soft constraints to keep counts near the target
            target = int(target_courses_per_day)
            for day_idx, day_count in enumerate(day_counts):
                # Create variables for above and below target
                above_target = self.model.NewIntVar(0, len(group_courses), f'above_target_{group_name}_{day_idx}')
                below_target = self.model.NewIntVar(0, len(group_courses), f'below_target_{group_name}_{day_idx}')
                
                # Link them to the actual count
                self.model.Add(day_count - target == above_target - below_target)
                
                # Add both to penalties
                self.balance_penalties.append(above_target)
                self.balance_penalties.append(below_target)


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
            for _, courses in self.variables.items():
                for _, course in courses.items():
                    for _, details in course.items():
                        print(f"{details['subject']} | {details['timeslot']}: {self.solver.value(details['timeslot'])} | {details['room']}: {self.solver.value(details['room'])}")            
        else:
            print("No solution found.")

        print(f"Computational time: {round((time.time()-start_time),3)} s")
