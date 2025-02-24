from .objects import *
from ortools.sat.python import cp_model
import yaml # Nested dictionnary pretty print purposes
import time
import sys
import threading
import psutil
import os

# Schedule Intel imports
from collections import defaultdict
from typing import Dict, List, Any

class ChronometerCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, model, conflict_penalties, test=False):
        super().__init__()
        self.start_time = time.time()
        self.running = True
        self.paused = False
        self.pause_time = 0
        self.accumulated_pause_time = 0
        self.thread = threading.Thread(target=self.update_timer, daemon=True)
        self.thread.start()
        self.model = model
        self.conflict_penalties = conflict_penalties
        self.found_feasible = False
        self.continue_search = True
        self.max_cpu = 0
        self.max_ram = 0
        self.test = test

    def update_timer(self):
        """Continuously update elapsed time every second until stopped."""
        while self.running:
            if not self.paused:
                elapsed = time.time() - self.start_time - self.accumulated_pause_time
                process = psutil.Process(os.getpid())  # Get current process
                ram_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                cpu_usage = process.cpu_percent(interval=0.1)/10 # CPU usage (%)
                if(ram_usage > self.max_ram):
                    self.max_ram = ram_usage
                if(cpu_usage > self.max_cpu):
                    self.max_cpu = cpu_usage
                sys.stdout.write(f"\rElapsed time: {elapsed:.2f} s | CPU : {cpu_usage:.2f} % | RAM {ram_usage:.2f} Mb | Peak CPU : {self.max_cpu:.2f} % | Max RAM : {self.max_ram:.2f} Mb      ")
                sys.stdout.flush()
            time.sleep(1)  # Update every second

    def pause_chronometer(self):
        """Pause the chronometer."""
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()

    def resume_chronometer(self):
        """Resume the chronometer."""
        if self.paused:
            self.accumulated_pause_time += time.time() - self.pause_time
            self.paused = False

    def OnSolutionCallback(self):
        """Update elapsed time when a solution is found."""
        if not self.paused:
            elapsed = time.time() - self.start_time - self.accumulated_pause_time
            sys.stdout.write(f"\rElapsed time: {elapsed:.2f} s")
            sys.stdout.flush()
        
        # Check if this solution has no conflicts
        has_conflicts = False
        for penalty in self.conflict_penalties:
            if isinstance(penalty, cp_model.IntVar):
                if self.Value(penalty) > 0:
                    has_conflicts = True
                    break
            elif isinstance(penalty, cp_model.BoolVar):
                if self.Value(penalty):
                    has_conflicts = True
                    break
        
        if not has_conflicts and not self.found_feasible:
            self.found_feasible = True
            self.pause_chronometer()
            print("\nFound a feasible solution without conflicts!")
            if self.test == True:
                self.continue_search = False
                self.StopSearch()
            else:
                time.sleep(2)
                user_input = input("Stop search and use this solution? (y/n): ")
                if user_input.lower() == 'y':
                    self.continue_search = False
                    self.StopSearch()
                self.resume_chronometer()

    def EndSearch(self):
        """Stop the chronometer and ensure the final time is displayed."""
        self.running = False  # Stop the loop
        self.thread.join(timeout=1)  # Ensure the thread stops (with a small timeout)
        elapsed = time.time() - self.start_time - self.accumulated_pause_time
        print(f"\nTotal solving time: {elapsed:.2f} s")

class ScheduleIntelligence:
    def __init__(self, generated_courses: List[Course], university: University):
        self.courses = generated_courses
        self.university = university
        self.intel = {
            'conflicts': {
                'room_overlaps': [],
                'teacher_overlaps': [],
                'timeslot_conflicts': []
            },
            'resource_utilization': {
                'rooms': defaultdict(list),
                'teachers': defaultdict(list),
                'timeslots': defaultdict(int)
            },
            'course_distribution': {
                'by_subject': defaultdict(list),
                'by_group': defaultdict(list)
            }
        }
    
    def analyze_conflicts(self):
        """Detect and log scheduling conflicts."""
        # Sort courses by timeslot using university's timeslots list
        timeslot_order = self.university.timeslots
        sorted_courses = sorted(
            self.courses, 
            key=lambda x: timeslot_order.index(x.timeslot)
        )
        
        for i, course1 in enumerate(sorted_courses):
            for course2 in sorted_courses[i+1:]:
                # Room Overlap Detection
                if (course1.timeslot == course2.timeslot and 
                    course1.room == course2.room and 
                    course1.room.name.lower() != "online" and course2.room.name.lower() != "online"):
                    self.intel['conflicts']['room_overlaps'].append({
                        'courses': [
                            {'subject': course1.subject.name, 'group': course1.group.name},
                            {'subject': course2.subject.name, 'group': course2.group.name}
                        ],
                        'timeslot': timeslot_order.index(course1.timeslot),
                        'room': course1.room.name
                    })
                
                # Teacher Overlap Detection
                if (course1.timeslot == course2.timeslot and 
                    course1.teacher == course2.teacher):
                    self.intel['conflicts']['teacher_overlaps'].append({
                        'courses': [
                            {'subject': course1.subject.name, 'group': course1.group.name},
                            {'subject': course2.subject.name, 'group': course2.group.name}
                        ],
                        'timeslot': timeslot_order.index(course1.timeslot),
                        'teacher': course1.teacher.last_name
                    })
    
    def analyze_resource_utilization(self):
        """Analyze how resources are being used."""
        timeslot_order = self.university.timeslots
        
        for course in self.courses:
            timeslot_index = timeslot_order.index(course.timeslot)
            
            # Room utilization
            self.intel['resource_utilization']['rooms'][course.room.name].append({
                'subject': course.subject.name,
                'group': course.group.name,
                'timeslot': timeslot_index
            })
            
            # Teacher utilization
            self.intel['resource_utilization']['teachers'][course.teacher.last_name].append({
                'subject': course.subject.name,
                'group': course.group.name,
                'timeslot': timeslot_index
            })
            
            # Timeslot utilization
            self.intel['resource_utilization']['timeslots'][timeslot_index] += 1
            
            # Course distribution
            self.intel['course_distribution']['by_subject'][course.subject.name].append({
                'group': course.group.name,
                'timeslot': timeslot_index,
                'room': course.room.name
            })
            
            self.intel['course_distribution']['by_group'][course.group.name].append({
                'subject': course.subject.name,
                'timeslot': timeslot_index,
                'room': course.room.name
            })
    
    def generate_report(self):
        """Generate a comprehensive scheduling intelligence report."""
        print("\n==== SCHEDULING INTELLIGENCE REPORT ====")
        
        # Conflict Summary
        print("\n1. CONFLICT ANALYSIS")
        print(f"   - Room Overlaps: {len(self.intel['conflicts']['room_overlaps'])}")
        for overlap in self.intel['conflicts']['room_overlaps']:
            print(f"     * Timeslot {overlap['timeslot']}, Room {overlap['room']}:")
            for course in overlap['courses']:
                print(f"       - {course['subject']} ({course['group']})")
        
        print(f"   - Teacher Overlaps: {len(self.intel['conflicts']['teacher_overlaps'])}")
        for overlap in self.intel['conflicts']['teacher_overlaps']:
            print(f"     * Timeslot {overlap['timeslot']}, Teacher {overlap['teacher']}:")
            for course in overlap['courses']:
                print(f"       - {course['subject']} ({course['group']})")
        
        # Resource Utilization
        print("\n2. RESOURCE UTILIZATION")
        print("   Top 3 Most Used Rooms:")
        room_usage = sorted(
            self.intel['resource_utilization']['rooms'].items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:3]
        for room, courses in room_usage:
            print(f"     * {room}: {len(courses)} courses")
        
        print("   Top 3 Most Used Teachers:")
        teacher_usage = sorted(
            self.intel['resource_utilization']['teachers'].items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:3]
        for teacher, courses in teacher_usage:
            print(f"     * {teacher}: {len(courses)} courses")
        
        # Timeslot Distribution
        print("\n3. TIMESLOT DISTRIBUTION")
        sorted_timeslots = sorted(
            self.intel['resource_utilization']['timeslots'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        print("   Top 3 Most Used Timeslots:")
        for timeslot, count in sorted_timeslots[:3]:
            print(f"     * Timeslot {timeslot}: {count} courses")
        
        print("\n==== END OF INTELLIGENCE REPORT ====")


class CSP:
    def __init__(self, university: University, test = False):
        self.university = university
        self.model = cp_model.CpModel()
        self.variables = {}  # Dictionary to store variables for each course
        self.generated_courses: List[Course] = []  # List of all generated courses
        self.solver = cp_model.CpSolver()
        self.chronometer = None
        self.test = test

        # Store objective terms
        self.gap_penalties = []  # For storing gap penalties
        self.balance_penalties = []  # For storing balance penalties
        self.conflict_penalties = []  # For storing conflict penalties

        print("Generating the variables...")
        self.createVariables()
        print("Created the variables.")
        #self.printVariables()
        print("Creating the constraints...")
        self.createConstraints()
        self.createSoftConstraints()
        print("Created the constraints")
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
        print(" - Room overlaps ...")
        self.noRoomOverlap()
        print(" - Max 30% online hours")
        self.limit_online_hours()
        print(" - Courses overlaps ...")
        self.noMultipleCoursesOnTimeslotForGroup()
        print(" - Teacher overlaps ...")
        self.noTeacherOverlap()
        print(" - Teacher availability ...")
        self.teacherAvailabilityConstraint()
        print(" - Lunch break ...")
        self.ensureLunchBreak()
        print(" - Weekends restrictions ...")
        self.restrictWeekendTimeslots()

    def createSoftConstraints(self):
        print(" - Balanced courses ...")
        # Balance courses across days
        self.balanceCoursesAcrossDays()
        
        # Combine different penalty types
        penalties = []
        if self.balance_penalties:
            penalties.extend(self.balance_penalties)
        if self.conflict_penalties:
            penalties.extend(self.conflict_penalties)
        
        # Minimize total penalties
        if penalties:
            total_cost = sum(penalties)
            self.model.Minimize(total_cost)

    def noRoomOverlap(self):
        # First, find if there's an online room and get its index
        online_room_index = None
        for i, room in enumerate(self.university.rooms):
            if room.name.lower() == "online":
                online_room_index = i
                break

        # Get all courses
        courses = []
        for _, group in self.variables.items():
            for _, subject in group.items():
                for course_key, course in subject.items():
                    courses.append(course)

        # Handle room overlap constraints
        for i in range(len(courses)):
            print(f" - - Course {i+1}/{len(courses)}", end="\r")
            for j in range(i + 1, len(courses)):
                same_timeslot = self.model.NewBoolVar(f'same_timeslot_{i}_{j}')
                self.model.Add(courses[i]['timeslot'] == courses[j]['timeslot']).OnlyEnforceIf(same_timeslot)
                self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot']).OnlyEnforceIf(same_timeslot.Not())
                
                same_room = self.model.NewBoolVar(f'same_room_{i}_{j}')
                self.model.Add(courses[i]['room'] == courses[j]['room']).OnlyEnforceIf(same_room)
                self.model.Add(courses[i]['room'] != courses[j]['room']).OnlyEnforceIf(same_room.Not())
                
                # Only add room conflict penalty if neither course is in an online room
                if online_room_index is not None:
                    course1_online = self.model.NewBoolVar(f'course1_online_{i}_{j}')
                    course2_online = self.model.NewBoolVar(f'course2_online_{i}_{j}')
                    
                    self.model.Add(courses[i]['room'] == online_room_index).OnlyEnforceIf(course1_online)
                    self.model.Add(courses[i]['room'] != online_room_index).OnlyEnforceIf(course1_online.Not())
                    self.model.Add(courses[j]['room'] == online_room_index).OnlyEnforceIf(course2_online)
                    self.model.Add(courses[j]['room'] != online_room_index).OnlyEnforceIf(course2_online.Not())
                    
                    # Add conflict penalty only if neither course is online
                    conflict_penalty = self.model.NewBoolVar(f'room_conflict_{i}_{j}')
                    self.model.AddBoolAnd([
                        same_timeslot, 
                        same_room, 
                        course1_online.Not(), 
                        course2_online.Not()
                    ]).OnlyEnforceIf(conflict_penalty)
                    self.model.AddBoolOr([
                        same_timeslot.Not(), 
                        same_room.Not(), 
                        course1_online, 
                        course2_online
                    ]).OnlyEnforceIf(conflict_penalty.Not())
                else:
                    # If no online room exists, use original conflict logic
                    conflict_penalty = self.model.NewBoolVar(f'room_conflict_{i}_{j}')
                    self.model.AddBoolAnd([same_timeslot, same_room]).OnlyEnforceIf(conflict_penalty)
                    self.model.AddBoolOr([same_timeslot.Not(), same_room.Not()]).OnlyEnforceIf(conflict_penalty.Not())
                
                self.conflict_penalties.append(conflict_penalty)

        print("")  # New line after progress indicator

    def limit_online_hours(self):
        # Identify the index of the "online" room
        online_room_index = None
        for i, room in enumerate(self.university.rooms):
            if room.name.lower() == "online":
                online_room_index = i
                print(" - - Courses can take place online.")
                break
        
        if online_room_index is None:
            print(" - - Courses can't take place online.")
            return
        
        if online_room_index is not None:
            for group_name, subjects in self.variables.items():
                for subject_name, courses in subjects.items():
                    total_courses = len(courses)
                    max_online_courses = int(0.3 * total_courses)  # 30% limit
                    
                    # Create a boolean variable for each course being online
                    online_vars = []
                    for course in courses.values():
                        is_online = self.model.NewBoolVar(f"is_online_{group_name}_{subject_name}_{id(course)}")
                        self.model.Add(course['room'] == online_room_index).OnlyEnforceIf(is_online)
                        self.model.Add(course['room'] != online_room_index).OnlyEnforceIf(is_online.Not())
                        online_vars.append(is_online)
                    
                    # Limit the number of online courses
                    self.model.Add(sum(online_vars) <= max_online_courses)
            
            print(" - - Online hours limit constraint added.")

    def noMultipleCoursesOnTimeslotForGroup(self):
        total_constraints = 0
        courses = []
        for _, group in self.variables.items():
            # Group is a Tuple with : (group name, corresponding items)
            for _, subject in group.items():
                # Subject is a Tuple with : (subject name, corresponding items)
                for course_key, course in subject.items():
                    courses.append(course)

        for i in range(len(courses)):
            print(f" - - Course {i+1}/{len(courses)}", end="\r")
            for j in range(i + 1, len(courses)):
                # Check if the groups are the same
                if courses[i]['group'] == courses[j]['group']:
                    # Add constraint: courses in the same group cannot share the same timeslot
                    self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot'])
                    total_constraints += 1
        
        print(f" - - Added {total_constraints} constraints")

    def noTeacherOverlap(self):
        courses = []
        for _, group in self.variables.items():
            for _, subject in group.items():
                for _, course in subject.items():
                    courses.append(course)

        for i in range(len(courses)):
            print(f" - - Course {i+1}/{len(courses)}", end="\r")
            for j in range(i + 1, len(courses)):
                same_timeslot = self.model.NewBoolVar(f'same_timeslot_teacher_{i}_{j}')
                self.model.Add(courses[i]['timeslot'] == courses[j]['timeslot']).OnlyEnforceIf(same_timeslot)
                self.model.Add(courses[i]['timeslot'] != courses[j]['timeslot']).OnlyEnforceIf(same_timeslot.Not())

                same_teacher = self.model.NewBoolVar(f'same_teacher_{i}_{j}')
                self.model.Add(courses[i]['teacher'] == courses[j]['teacher']).OnlyEnforceIf(same_teacher)
                self.model.Add(courses[i]['teacher'] != courses[j]['teacher']).OnlyEnforceIf(same_teacher.Not())

                # Add penalty when same timeslot AND same teacher
                conflict_penalty = self.model.NewBoolVar(f'teacher_conflict_{i}_{j}')
                self.model.AddBoolAnd([same_timeslot, same_teacher]).OnlyEnforceIf(conflict_penalty)
                self.model.AddBoolOr([same_timeslot.Not(), same_teacher.Not()]).OnlyEnforceIf(conflict_penalty.Not())
                
                self.conflict_penalties.append(conflict_penalty)
        
        print("")

    def teacherAvailabilityConstraint(self):
        """
        Ensures teachers are only assigned to courses during their available timeslots.
        """
        courses = []
        for _, group in self.variables.items():
            for _, subject in group.items():
                for _, course in subject.items():
                    courses.append(course)

        for k, course in enumerate(courses):
            print(f" - - Course {k+1}/{len(courses)}", end="\r")
            teacher_var = course['teacher']
            timeslot_var = course['timeslot']

            # For each potential teacher
            for teacher_idx, teacher in enumerate(self.university.teachers):
                if hasattr(teacher, 'available_slots') and teacher.available_slots:
                    # Directly enforce that if a teacher is selected, the timeslot must be in their available slots
                    for ts_idx in range(len(self.university.timeslots)):
                        if ts_idx not in teacher.available_slots:
                            self.model.AddImplication(teacher_var == teacher_idx, timeslot_var != ts_idx)

        print("")

    def ensureLunchBreak(self):
        total_constraints = 0

        # Define the lunch break timeslot indices (11:30 -> 13:15), where index % 7 == 2
        lunch_break_timeslots = [index for index, _ in enumerate(self.university.timeslots) if index % 7 == 2]

        # Collect all course timeslot variables
        all_timeslot_vars = [
            course['timeslot']
            for subjects in self.variables.values()
            for subject_courses in subjects.values()
            for course in subject_courses.values()
        ]

        # Apply forbidden assignments for each variable individually
        for var in all_timeslot_vars:
            self.model.AddForbiddenAssignments([var], [[slot] for slot in lunch_break_timeslots])
            total_constraints += 1

        print(f" - - Excluded {len(lunch_break_timeslots)} lunch break timeslots for {len(all_timeslot_vars)} courses")
        print(f" - - Added {total_constraints} constraints")

    def restrictWeekendTimeslots(self):
        """
        Ensures no courses are scheduled during weekend slots:
        - After the 3rd timeslot on Saturday (timeslots 3-6 of each Saturday)
        - All day Sunday (timeslots 0-6 of each Sunday)
        Works for any week in the schedule.
        """
        # Get all courses from all groups
        all_courses = []
        for group_courses in self.variables.values():
            for subject_courses in group_courses.values():
                all_courses.extend(subject_courses.values())
        
        # For each course, add constraints for weekend restrictions
        for course in all_courses:
            timeslot_var = course['timeslot']
            
            solts_per_days = int(len(self.university.time_ranges))
            # Create intermediate variables for the modulo operations
            week_day = self.model.NewIntVar(0, 6, f'week_day_{id(course)}')  # 0-6 for days of week
            day_slot = self.model.NewIntVar(0, solts_per_days, f'day_slot_{id(course)}')  # slots within day
            
            # Use AddModuloEquality for both operations
            # First get the slot within the day
            self.model.AddModuloEquality(day_slot, timeslot_var, solts_per_days)
            
            # Then get the day of week (after dividing by the number of slots per day)
            timeslot_div = self.model.NewIntVar(0, len(self.university.timeslots), f'timeslot_div_{id(course)}')
            self.model.AddDivisionEquality(timeslot_div, timeslot_var, solts_per_days)
            self.model.AddModuloEquality(week_day, timeslot_div, solts_per_days)
            
            # Create constraints for Saturday afternoon (day 5, slots 3-6)
            is_saturday = self.model.NewBoolVar(f'is_saturday_{id(course)}')
            is_afternoon = self.model.NewBoolVar(f'is_afternoon_{id(course)}')
            
            self.model.Add(week_day == 5).OnlyEnforceIf(is_saturday)
            self.model.Add(week_day != 5).OnlyEnforceIf(is_saturday.Not())
            
            self.model.Add(day_slot >= 3).OnlyEnforceIf(is_afternoon)
            self.model.Add(day_slot < 3).OnlyEnforceIf(is_afternoon.Not())
            
            # If both conditions are true, this is a Saturday afternoon slot
            is_saturday_afternoon = self.model.NewBoolVar(f'is_saturday_afternoon_{id(course)}')
            self.model.AddBoolAnd([is_saturday, is_afternoon]).OnlyEnforceIf(is_saturday_afternoon)
            self.model.AddBoolOr([is_saturday.Not(), is_afternoon.Not()]).OnlyEnforceIf(is_saturday_afternoon.Not())
            
            # Create constraint for Sunday (day 6)
            is_sunday = self.model.NewBoolVar(f'is_sunday_{id(course)}')
            self.model.Add(week_day == 6).OnlyEnforceIf(is_sunday)
            self.model.Add(week_day != 6).OnlyEnforceIf(is_sunday.Not())
            
            # Forbid both Saturday afternoon and Sunday slots
            self.model.Add(is_saturday_afternoon == 0)
            self.model.Add(is_sunday == 0)

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
        """Enhanced solve method with comprehensive conflict tracking."""
        start_time = time.time()

        # Configure solver for flexibility
        import multiprocessing
        #int(multiprocessing.cpu_count()/2)
        if int(multiprocessing.cpu_count()) >= 4:
            worknum = 4
        else:
            worknum = multiprocessing.cpu_count()/2
        self.solver.parameters.num_search_workers = worknum # int(multiprocessing.cpu_count()/2)
        print(f"Using {worknum} cores")
        if(self.test):
            max_time = 1200
        else:
            try:
                max_time = int(input("How many seconds should the solver run for (max):\n"))
            except:
                print("You didn't gave a correct integer value. Max time set to 1200 seconds.")
                max_time = 1200
                
        self.solver.parameters.max_time_in_seconds = max_time

        print(f"\nInstance generated, solving the CSP...")
        self.chronometer = ChronometerCallback(self.model, self.conflict_penalties, self.test)
        status = self.solver.Solve(self.model, self.chronometer)
        self.chronometer.running = False

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            if status == cp_model.OPTIMAL:
                print("\nOptimal solution found:")
            else:
                print("\nSub-optimal feasible solution found:")            
            self.variablesToCourses()
            
            # Print course assignments (debug)
            #for _, courses in self.variables.items():
            #    for _, course in courses.items():
            #        for _, details in course.items():
            #            print(f"{details['subject']} | Timeslot: {self.solver.Value(details['timeslot'])} | Room: {self.solver.Value(details['room'])}")
            
            # Perform schedule intelligence analysis
            try:
                schedule_intel = ScheduleIntelligence(self.generated_courses, self.university)
                schedule_intel.analyze_conflicts()
                schedule_intel.analyze_resource_utilization()
                schedule_intel.generate_report()
            except Exception as e:
                print(f"Error in schedule intelligence analysis: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No complete solution found. Please retry giving the CSP more time !")
            print("If time limit wasn't reached, this might mean that the instance is inconsistent and that no solution can be found !")
            print(" -> You may want to modify the instance of your problem (adding more days...)")
        
        print(f"Computational time: {round((time.time()-start_time),3)} s")

        return self.generated_courses