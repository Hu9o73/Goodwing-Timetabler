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
    def __init__(self, model, conflict_penalties, balance_penalties=None, gap_penalties=None, test=False):
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
        self.balance_penalties = balance_penalties or []
        self.gap_penalties = gap_penalties or []
        self.found_feasible = False
        self.continue_search = True
        self.max_cpu = 0
        self.max_ram = 0
        self.test = test
        self.best_objective = float('inf')  # Track best objective value
        self.solution_count = 0  # Track number of solutions found

    def update_timer(self):
        """Continuously update elapsed time every second until stopped."""
        max_line_length = 0  # Track maximum line length
        
        while self.running:
            if not self.paused:
                elapsed = time.time() - self.start_time - self.accumulated_pause_time
                process = psutil.Process(os.getpid())  # Get current process
                ram_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                cpu_usage = process.cpu_percent(interval=0.1)/10  # CPU usage (%)
                
                if ram_usage > self.max_ram:
                    self.max_ram = ram_usage
                if cpu_usage > self.max_cpu:
                    self.max_cpu = cpu_usage
                
                # Display with current objective value if available
                objective_info = f"| Objective: {self.best_objective if self.best_objective != float('inf') else 'N/A'}"
                solutions_info = f"| Solutions: {self.solution_count}"
                
                # Create the status line
                status_line = f"Elapsed time: {elapsed:.2f}s | CPU: {cpu_usage:.2f}% | RAM: {ram_usage:.2f}MB | Peak CPU: {self.max_cpu:.2f}% | Max RAM: {self.max_ram:.2f}MB {objective_info} {solutions_info}"
                
                # Ensure line is at least as long as previous lines by padding with spaces
                if len(status_line) < max_line_length:
                    status_line += ' ' * (max_line_length - len(status_line))
                else:
                    max_line_length = len(status_line)
                
                # Try to use shutil to get terminal width if available
                try:
                    import shutil
                    term_width = shutil.get_terminal_size().columns
                    # Clear the entire line
                    clear_line = '\r' + ' ' * term_width + '\r'
                    sys.stdout.write(clear_line + status_line)
                except (ImportError, AttributeError):
                    # Fall back to simpler method if shutil is not available
                    sys.stdout.write('\r' + status_line)
                
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
        """Update elapsed time and objective value when a solution is found."""
        self.solution_count += 1
        
        # Calculate the objective value (sum of all penalties)
        current_objective = 0
        
        # Sum conflict penalties
        for penalty in self.conflict_penalties:
            if isinstance(penalty, cp_model.IntVar):
                current_objective += self.Value(penalty)
            elif isinstance(penalty, cp_model.BoolVar):
                current_objective += 1 if self.Value(penalty) else 0
        
        # Sum balance penalties
        for penalty in self.balance_penalties:
            current_objective += self.Value(penalty)
        
        # Sum gap penalties
        for penalty in self.gap_penalties:
            current_objective += self.Value(penalty)
        
        # Update best objective if this solution is better
        if current_objective < self.best_objective:
            self.best_objective = current_objective
        
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
            print(f"\nFound a feasible solution without conflicts! Objective value: {current_objective}")
            if self.test == True:
                self.continue_search = False
                self.StopSearch()
            else:
                time.sleep(2)
                user_input = input("\nStop search and use this solution? (y/n): ")
                if user_input.lower() == 'y':
                    self.continue_search = False
                    self.StopSearch()
                self.resume_chronometer()

    def EndSearch(self):
        """Stop the chronometer and ensure the final time is displayed."""
        self.running = False  # Stop the loop
        self.thread.join(timeout=1)  # Ensure the thread stops (with a small timeout)
        elapsed = time.time() - self.start_time - self.accumulated_pause_time
        print(f"\nTotal solving time: {elapsed:.2f}s | Final objective value: {self.best_objective}")

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
        self.output_dir = "Outputs"
        self.file_name = "intelligence_report.txt"
        self.file_path = os.path.join(self.output_dir, self.file_name)
    
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
    
    def analyze_penalty_breakdown(self, solver, csp_obj):
        """
        Analyzes the breakdown of penalties in the final solution.
        
        Args:
            solver: The CP-SAT solver after solving
            csp_obj: The CSP object with penalty lists
        """
        # Initialize counters for each penalty type
        conflict_penalty_sum = 0
        balance_penalty_sum = 0
        gap_penalty_sum = 0
        
        # Sum conflict penalties
        print("\n4. PENALTY BREAKDOWN")
        self.append_to_report("\n\n4. PENALTY BREAKDOWN")
        for penalty in csp_obj.conflict_penalties:
            if isinstance(penalty, cp_model.IntVar):
                conflict_penalty_sum += solver.Value(penalty)
            elif isinstance(penalty, cp_model.BoolVar):
                conflict_penalty_sum += 1 if solver.Value(penalty) else 0
        
        # Sum balance penalties
        for penalty in csp_obj.balance_penalties:
            balance_penalty_sum += solver.Value(penalty)
        
        # Sum gap penalties
        for penalty in csp_obj.gap_penalties:
            gap_penalty_sum += solver.Value(penalty)
        
        # Calculate total penalty
        total_penalty = conflict_penalty_sum + balance_penalty_sum + gap_penalty_sum
        
        # Display breakdown
        print(f"   - Conflict Penalties: {conflict_penalty_sum} ({(conflict_penalty_sum/total_penalty*100):.1f}% of total)")
        self.append_to_report(f"\n   - Conflict Penalties: {conflict_penalty_sum} ({(conflict_penalty_sum/total_penalty*100):.1f}% of total)")
        print(f"   - Balance Penalties: {balance_penalty_sum} ({(balance_penalty_sum/total_penalty*100):.1f}% of total)")
        self.append_to_report(f"\n   - Balance Penalties: {balance_penalty_sum} ({(balance_penalty_sum/total_penalty*100):.1f}% of total)")
        print(f"   - Gap Penalties: {gap_penalty_sum} ({(gap_penalty_sum/total_penalty*100):.1f}% of total)")
        self.append_to_report(f"\n   - Gap Penalties: {gap_penalty_sum} ({(gap_penalty_sum/total_penalty*100):.1f}% of total)")
        print(f"   - Total Objective Value: {total_penalty}")
        self.append_to_report(f"\n   - Total Objective Value: {total_penalty}")
        
        # Display guidance
        if gap_penalty_sum > 0:
            print("\n   Gap Improvement Opportunities:")
            self.append_to_report("\n\n   Gap Improvement Opportunities:")
            self._analyze_gaps(csp_obj)
        
        # Analyze online transitions
        self.analyze_online_transitions(csp_obj)
        
        # Analyze late timeslots
        self.analyze_late_slots(csp_obj)
        
        # Print the end of the intelligence report after all analysis
        print("\n==== END OF INTELLIGENCE REPORT ====")
        self.append_to_report("\n\n\n==== END OF INTELLIGENCE REPORT ====")

    def _analyze_gaps(self, csp_obj):
        """
        Analyzes where gaps occur most frequently to suggest improvements.
        Uses exactly the same definition of gaps as the minimizeGaps function.
        Lunch break slots are not counted as gaps.
        """
        # Group courses by day for each group
        day_courses = defaultdict(lambda: defaultdict(list))
        slots_per_day = len(self.university.time_ranges)
        
        # Define lunch break slot index (index % slots_per_day == 2)
        lunch_slot = 2
        
        # Debug findings list
        gap_findings = []
        
        for course in self.courses:
            group_name = course.group.name
            timeslot_idx = self.university.timeslots.index(course.timeslot)
            day_idx = timeslot_idx // slots_per_day
            slot_offset = timeslot_idx % slots_per_day
            
            # Skip lunch slots
            if slot_offset == lunch_slot:
                continue
            
            day_courses[group_name][day_idx].append(slot_offset)
        
        # Find days with gaps
        for group_name, days in day_courses.items():
            for day_idx, slots in days.items():
                # Must have at least 2 scheduled courses to have gaps
                if len(slots) >= 2:
                    slots.sort()
                    first_slot = min(slots)
                    last_slot = max(slots)
                    
                    # Calculate the span (excluding lunch break)
                    span = []
                    for i in range(first_slot, last_slot + 1):
                        if i != lunch_slot:  # Skip lunch slot
                            span.append(i)
                    
                    # Calculate gaps (slots in span that aren't used)
                    gaps = [i for i in span if i not in slots]
                    
                    if gaps:
                        day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_idx % 7]
                        week_num = day_idx // 7 + 1
                        
                        gap_times = []
                        for gap in gaps:
                            time_range = self.university.time_ranges[gap]
                            start_time = time_range[0].strftime("%H:%M")
                            end_time = time_range[1].strftime("%H:%M")
                            gap_times.append(f"{start_time}-{end_time}")
                        
                        # Store finding
                        gap_findings.append(f"Group {group_name}, Week {week_num} {day_name}: {len(gaps)} gap(s) at {', '.join(gap_times)}")
        
        # Print findings
        if gap_findings:
            print("\n   Gaps found in schedule (but not penalized):")
            self.append_to_report("\n\n   Gaps found in schedule (but not penalized):")
            for finding in gap_findings:
                print(f"     * {finding}")
                self.append_to_report(f"\n     * {finding}")
            print("\n   This could indicate that the gap minimization is not working correctly.")
            self.append_to_report("\n\n   This could indicate that the gap minimization is not working correctly.")
        else:
            print("   No gaps found in the schedule - gap minimization is working correctly.")
            self.append_to_report("\n   No gaps found in the schedule - gap minimization is working correctly.")

    def analyze_online_transitions(self, csp_obj):
        """
        Analyzes the final schedule to identify any remaining online-to-physical transitions.
        Adds a new section to the intelligence report with this information.
        """
        # Find the online room
        online_room = None
        for room in self.university.rooms:
            if room.name.lower() == "online":
                online_room = room
                break
        
        if not online_room:
            print("\n5. ONLINE-PHYSICAL TRANSITIONS")
            self.append_to_report("\n\n5. ONLINE-PHYSICAL TRANSITIONS")
            print("   No online room found in the university instance.")
            self.append_to_report("\n   No online room found in the university instance.")
            return
        
        print("\n5. ONLINE-PHYSICAL TRANSITIONS")
        self.append_to_report("\n\n5. ONLINE-PHYSICAL TRANSITIONS")
        
        # Group courses by group and day
        group_day_courses = defaultdict(lambda: defaultdict(list))
        slots_per_day = len(self.university.time_ranges)
        
        for course in self.courses:
            group_name = course.group.name
            timeslot_idx = self.university.timeslots.index(course.timeslot)
            day_idx = timeslot_idx // slots_per_day
            slot_within_day = timeslot_idx % slots_per_day
            
            # Add to appropriate group and day, sorted by timeslot
            group_day_courses[group_name][day_idx].append((slot_within_day, course))
        
        # Track transitions
        total_transitions = 0
        transition_details = []
        
        # Check each group's daily schedule for transitions
        for group_name, days in group_day_courses.items():
            group_transitions = 0
            
            for day_idx, courses in days.items():
                # Sort courses by timeslot within the day
                sorted_courses = sorted(courses, key=lambda x: x[0])
                
                # Check for transitions
                for i in range(len(sorted_courses) - 1):
                    current_slot, current_course = sorted_courses[i]
                    next_slot, next_course = sorted_courses[i + 1]
                    
                    # Only check consecutive slots
                    if next_slot == current_slot + 1:
                        current_is_online = current_course.room.name.lower() == "online"
                        next_is_online = next_course.room.name.lower() == "online"
                        
                        # If there's a transition
                        if current_is_online != next_is_online:
                            total_transitions += 1
                            group_transitions += 1
                            
                            # Determine the direction
                            direction = "Online → Physical" if current_is_online else "Physical → Online"
                            
                            # Get day name
                            day_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day_idx % 7]
                            week_num = day_idx // 7 + 1
                            
                            # Format times
                            current_time = f"{self.format_time(current_course.timeslot.start)}-{self.format_time(current_course.timeslot.end)}"
                            next_time = f"{self.format_time(next_course.timeslot.start)}-{self.format_time(next_course.timeslot.end)}"
                            
                            # Add to details
                            transition_details.append({
                                'group': group_name,
                                'day': f"Week {week_num} {day_of_week}",
                                'direction': direction,
                                'from_course': f"{current_course.subject.name} ({current_time})",
                                'to_course': f"{next_course.subject.name} ({next_time})"
                            })
            
            if group_transitions > 0:
                print(f"   - Group {group_name}: {group_transitions} transitions")
                self.append_to_report(f"\n   - Group {group_name}: {group_transitions} transitions")
        
        print(f"   - Total transitions in schedule: {total_transitions}")
        self.append_to_report(f"\n   - Total transitions in schedule: {total_transitions}")
        
        # If there are transitions, show details
        if transition_details:
            print("\n   Transition Details:")
            self.append_to_report("\n\n   Transition Details:")
            for i, detail in enumerate(transition_details[:10], 1):  # Show only first 10 to avoid overwhelming
                print(f"     {i}. {detail['group']} on {detail['day']}: {detail['direction']}")
                self.append_to_report(f"\n     {i}. {detail['group']} on {detail['day']}: {detail['direction']}")
                print(f"        From: {detail['from_course']}")
                self.append_to_report(f"\n        From: {detail['from_course']}")
                print(f"        To:   {detail['to_course']}")
                self.append_to_report(f"\n        To:   {detail['to_course']}")
            
            if len(transition_details) > 10:
                print(f"     ... and {len(transition_details) - 10} more transitions")
                self.append_to_report(f"\n     ... and {len(transition_details) - 10} more transitions")
        else:
            print("   No transitions found - online courses are optimally grouped!")
            self.append_to_report("\n   No transitions found - online courses are optimally grouped!")

    def format_time(self, time_obj):
        """Helper method to format time objects consistently"""
        return time_obj.strftime("%H:%M")
    
    def analyze_late_slots(self, csp_obj):
        """
        Analyzes the schedule to identify courses scheduled in the last two timeslots of each day.
        """
        print("\n6. LATE TIMESLOT ANALYSIS")
        self.append_to_report("\n\n6. LATE TIMESLOT ANALYSIS")
        
        # Number of timeslots per day
        slots_per_day = len(self.university.time_ranges)
        
        # Identify the last two timeslots of each day
        late_slot_offsets = [slots_per_day - 2, slots_per_day - 1]
        
        # Group courses by late timeslots
        late_courses = []
        late_by_group = defaultdict(int)
        
        for course in self.courses:
            timeslot_idx = self.university.timeslots.index(course.timeslot)
            day_idx = timeslot_idx // slots_per_day
            slot_offset = timeslot_idx % slots_per_day
            
            if slot_offset in late_slot_offsets:
                late_courses.append(course)
                late_by_group[course.group.name] += 1
        
        # Get the day names and times for better readability
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Get time ranges
        last_slots_times = []
        for offset in late_slot_offsets:
            if offset < len(self.university.time_ranges):
                time_range = self.university.time_ranges[offset]
                start_time = time_range[0].strftime("%H:%M")
                end_time = time_range[1].strftime("%H:%M")
                last_slots_times.append(f"{start_time}-{end_time}")
        
        # Report statistics
        total_courses = len(self.courses)
        late_course_count = len(late_courses)
        late_percentage = (late_course_count / total_courses * 100) if total_courses > 0 else 0
        
        print(f"   - Late timeslots: {', '.join(last_slots_times)}")
        self.append_to_report(f"\n   - Late timeslots: {', '.join(last_slots_times)}")
        print(f"   - Courses in late timeslots: {late_course_count} ({late_percentage:.1f}% of all courses)")
        self.append_to_report(f"\n   - Courses in late timeslots: {late_course_count} ({late_percentage:.1f}% of all courses)")
        
        # Report by group
        if late_by_group:
            print("\n   Distribution by group:")
            self.append_to_report("\n\n   Distribution by group:")
            for group_name, count in sorted(late_by_group.items(), key=lambda x: x[1], reverse=True):
                print(f"     - {group_name}: {count} late courses")
                self.append_to_report(f"\n     - {group_name}: {count} late courses")
        
        # List the first few late courses as examples
        if late_courses:
            print("\n   Sample late courses:")
            self.append_to_report("\n\n   Sample late courses:")
            for i, course in enumerate(late_courses[:5]):
                timeslot_idx = self.university.timeslots.index(course.timeslot)
                day_idx = timeslot_idx // slots_per_day
                day_name = day_names[day_idx % 7]
                week_num = day_idx // 7 + 1
                
                time_str = f"{course.timeslot.start.strftime('%H:%M')}-{course.timeslot.end.strftime('%H:%M')}"
                
                print(f"     {i+1}. {course.subject.name} for {course.group.name}")
                self.append_to_report(f"\n     {i+1}. {course.subject.name} for {course.group.name}")
                print(f"        Week {week_num} {day_name} at {time_str}")
                self.append_to_report(f"\n        Week {week_num} {day_name} at {time_str}")
                print(f"        Room: {course.room.name}, Teacher: {course.teacher.first_name} {course.teacher.last_name}")
                self.append_to_report(f"\n        Room: {course.room.name}, Teacher: {course.teacher.first_name} {course.teacher.last_name}")
            
            if len(late_courses) > 5:
                print(f"     ... and {len(late_courses) - 5} more late courses")
                self.append_to_report(f"\n     ... and {len(late_courses) - 5} more late courses")
        else:
            print("   No courses scheduled in late timeslots!")
            self.append_to_report("\n   No courses scheduled in late timeslots!")



    def append_to_report(self, text):
        """Appends text to the intelligence_report.txt file inside Outputs/"""
        with open(self.file_path, "a") as file:  # "a" mode appends without overwriting
            file.write(text)  # Ensure new lines for readability


    def generate_report(self):
        """Generate a comprehensive scheduling intelligence report."""

        # Clear the intelligence_report.txt file at the beginning of execution
        with open(self.file_path, "w") as file:
            file.write("")

        print("\n==== SCHEDULING INTELLIGENCE REPORT ====")
        self.append_to_report("==== SCHEDULING INTELLIGENCE REPORT ====")

        # Conflict Summary
        print("\n1. CONFLICT ANALYSIS")
        self.append_to_report("\n\n\n1. CONFLICT ANALYSIS")
        print(f"   - Room Overlaps: {len(self.intel['conflicts']['room_overlaps'])}")
        self.append_to_report(f"\n   - Room Overlaps: {len(self.intel['conflicts']['room_overlaps'])}")
        for overlap in self.intel['conflicts']['room_overlaps']:
            print(f"     * Timeslot {overlap['timeslot']}, Room {overlap['room']}:")
            self.append_to_report(f"\n     * Timeslot {overlap['timeslot']}, Room {overlap['room']}:")
            for course in overlap['courses']:
                print(f"       - {course['subject']} ({course['group']})")
                self.append_to_report(f"\n       - {course['subject']} ({course['group']})")
        
        print(f"   - Teacher Overlaps: {len(self.intel['conflicts']['teacher_overlaps'])}")
        self.append_to_report(f"\n   - Teacher Overlaps: {len(self.intel['conflicts']['teacher_overlaps'])}")
        for overlap in self.intel['conflicts']['teacher_overlaps']:
            print(f"     * Timeslot {overlap['timeslot']}, Teacher {overlap['teacher']}:")
            self.append_to_report(f"\n     * Timeslot {overlap['timeslot']}, Teacher {overlap['teacher']}:")
            for course in overlap['courses']:
                print(f"       - {course['subject']} ({course['group']})")
                self.append_to_report(f"\n       - {course['subject']} ({course['group']})")
        
        # Resource Utilization
        print("\n2. RESOURCE UTILIZATION")
        self.append_to_report("\n\n2. RESOURCE UTILIZATION")
        print("   Top 3 Most Used Rooms:")
        self.append_to_report("\n   Top 3 Most Used Rooms:")
        room_usage = sorted(
            self.intel['resource_utilization']['rooms'].items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:3]
        for room, courses in room_usage:
            print(f"     * {room}: {len(courses)} courses")
            self.append_to_report(f"\n     * {room}: {len(courses)} courses")
        
        print("   Top 3 Most Used Teachers:")
        self.append_to_report("\n   Top 3 Most Used Teachers:")
        teacher_usage = sorted(
            self.intel['resource_utilization']['teachers'].items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:3]
        for teacher, courses in teacher_usage:
            print(f"     * {teacher}: {len(courses)} courses")
            self.append_to_report(f"\n     * {teacher}: {len(courses)} courses")
        
        # Timeslot Distribution
        print("\n3. TIMESLOT DISTRIBUTION")
        self.append_to_report("\n\n3. TIMESLOT DISTRIBUTION")
        sorted_timeslots = sorted(
            self.intel['resource_utilization']['timeslots'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        print("   Top 3 Most Used Timeslots:")
        self.append_to_report("\n   Top 3 Most Used Timeslots:")
        for timeslot, count in sorted_timeslots[:3]:
            print(f"     * Timeslot {timeslot}: {count} courses")
            self.append_to_report(f"\n     * Timeslot {timeslot}: {count} courses")
        
        # Note: The penalty breakdown (section 4) will be added here by the analyze_penalty_breakdown method
        # which is called separately after this method. This ensures it's shown before the end of the report.
        
        # The end of the report is printed after the penalty breakdown is shown
        # The analyze_penalty_breakdown method is responsible for calling this


class CSP:
    def __init__(self, university: University, test = False):
        self.university = university
        self.model = cp_model.CpModel()
        self.variables = {}  # Dictionary to store variables for each course
        self.teacher_assignments = {}  # Dictionary to store teacher assignment variables per group and subject
        self.generated_courses: List[Course] = []  # List of all generated courses
        self.solver = cp_model.CpSolver()
        self.chronometer = None
        self.test = test

        self.output_dir = "Outputs"
        self.file_name = "intelligence_report.txt"
        self.file_path = os.path.join(self.output_dir, self.file_name)

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


    def append_to_report(self, text):
        """Appends text to the intelligence_report.txt file inside Outputs/"""
        with open(self.file_path, "a") as file:  # "a" mode appends without overwriting
            file.write(text)  # Ensure new lines for readability

    def createVariables(self):
        overall_course_idx = 0
        
        # First, create teacher assignment variables for each group-subject pair
        for promo in self.university.promotions:
            for group in promo.groups:
                if group.name not in self.teacher_assignments:
                    self.teacher_assignments[group.name] = {}
                
                for subject in promo.subjects:
                    # Filter teachers who can teach this subject
                    valid_teachers = [i for i, t in enumerate(self.university.teachers) if subject in t.subjects]
                    
                    if valid_teachers:  # Only create assignment if there are valid teachers
                        # Create a single teacher variable for all courses of this subject for this group
                        teacher_var = self.model.NewIntVarFromDomain(
                            cp_model.Domain.FromValues(valid_teachers),
                            f"teacher_assignment_{group.name}_{subject.name}"
                        )
                        self.teacher_assignments[group.name][subject.name] = teacher_var
        
        # Now create the course variables using the teacher assignments
        for promo in self.university.promotions:
            for group in promo.groups:
                self.variables[group.name] = {}
                for subject in promo.subjects:
                    self.variables[group.name][subject.name] = {}
                    
                    # Calculate number of timeslots needed for the subject
                    required_hours = subject.hours
                    timeslot_duration = self.university.timeslot_duration  # Assume in hours
                    num_courses = int(required_hours // timeslot_duration)
                    
                    for idx_course in range(num_courses):
                        overall_course_idx += 1
                        # Timeslot variable
                        timeslot_var = self.model.new_int_var(0, len(self.university.timeslots) - 1, f"course_{overall_course_idx}_timeslot")
                        
                        # Room variable
                        room_var = self.model.new_int_var(0, len(self.university.rooms) - 1, f"course_{overall_course_idx}_room")

                        # Create the variable (without a separate teacher variable per course)
                        self.variables[group.name][subject.name][overall_course_idx] = {
                            'subject': subject.name, 
                            'group': group.name, 
                            'timeslot': timeslot_var, 
                            'room': room_var
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
        print(" - Balanced subjects ...")
        # Balance individual subjects across weeks
        self.balanceSubjectsAcrossWeeks()
        print(" - Minimizing gaps ...")
        # Minimize gaps in daily schedules
        self.minimizeGaps()
        print(" - Minimizing campus returns after online classes ...")
        # Minimize students having to return to campus after online classes
        self.minimize_campus_returns()
        print(" - Minimizing late timeslots ...")
        # Minimize use of late timeslots
        self.minimize_late_slots()
        
        # Combine different penalty types
        penalties = []
        if self.balance_penalties:
            penalties.extend(self.balance_penalties)
        if self.conflict_penalties:
            penalties.extend(self.conflict_penalties)
        if self.gap_penalties:
            penalties.extend(self.gap_penalties)
        
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
        """
        Modified to use the group-subject teacher assignments instead of per-course assignments
        """
        courses = []
        for group_name, subjects in self.variables.items():
            for subject_name, subject_courses in subjects.items():
                for course_id, course in subject_courses.items():
                    # Only add if there's a teacher assignment for this group-subject
                    if group_name in self.teacher_assignments and subject_name in self.teacher_assignments[group_name]:
                        # Create a course entry with the teacher assignment
                        course_entry = course.copy()
                        course_entry['teacher'] = self.teacher_assignments[group_name][subject_name]
                        course_entry['id'] = course_id  # Store course ID for reference
                        courses.append(course_entry)

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
        This version works with the group-subject teacher assignment model.
        """
        courses = []
        for group_name, subjects in self.variables.items():
            for subject_name, subject_courses in subjects.items():
                # Only process if there's a teacher assignment for this group-subject
                if group_name in self.teacher_assignments and subject_name in self.teacher_assignments[group_name]:
                    teacher_var = self.teacher_assignments[group_name][subject_name]
                    
                    for course_id, course in subject_courses.items():
                        course_entry = course.copy()
                        course_entry['teacher'] = teacher_var
                        courses.append(course_entry)
        
        for k, course in enumerate(courses):
            print(f" - - Course {k+1}/{len(courses)}", end="\r")
            teacher_var = course['teacher']
            timeslot_var = course['timeslot']
            
            # For each teacher, create a boolean variable indicating if they are assigned to this course
            for teacher_idx, teacher in enumerate(self.university.teachers):
                is_assigned = self.model.NewBoolVar(f'teacher_{teacher_idx}_assigned_to_course_{id(course)}')
                self.model.Add(teacher_var == teacher_idx).OnlyEnforceIf(is_assigned)
                self.model.Add(teacher_var != teacher_idx).OnlyEnforceIf(is_assigned.Not())
                
                # If this teacher is assigned, ensure the timeslot is one they're available for
                if hasattr(teacher, 'available_slots') and teacher.available_slots:
                    # For each possible timeslot
                    for ts_idx in range(len(self.university.timeslots)):
                        # If this timeslot is not in available_slots, create a constraint
                        if ts_idx not in teacher.available_slots:
                            # If this teacher is assigned, this timeslot can't be used
                            self.model.Add(timeslot_var != ts_idx).OnlyEnforceIf(is_assigned)
        
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
        """
        Modified to use the group-subject teacher assignments
        """
        for group_name, subjects in self.variables.items():
            for subject_name, courses in subjects.items():
                # Get the assigned teacher for this group-subject pair
                teacher_var = None
                if group_name in self.teacher_assignments and subject_name in self.teacher_assignments[group_name]:
                    teacher_var = self.teacher_assignments[group_name][subject_name]
                    assigned_teacher_index = self.solver.Value(teacher_var)
                    assigned_teacher = self.university.teachers[assigned_teacher_index]
                else:
                    # Handle case where no teacher can teach this subject
                    print(f"Warning: No teacher assignment for {subject_name} in group {group_name}")
                    continue
                
                # Find the subject object
                subject = None
                for promo in self.university.promotions:
                    for sub in promo.subjects:
                        if sub.name == subject_name:
                            subject = sub
                            break
                    if subject:
                        break
                
                # Convert all courses for this group-subject pair
                for course_details in courses.values():
                    self.generated_courses.append(
                        Course(self.university.timeslots[self.solver.Value(course_details['timeslot'])], 
                              Group(course_details['group']), 
                              subject, 
                              assigned_teacher, 
                              self.university.rooms[self.solver.Value(course_details['room'])])
                    )

        #for course in self.generated_courses:
         #   print(course)                 

    def balanceSubjectsAcrossWeeks(self):
        """
        Adds soft constraints to balance subject courses across available weeks.
        This prevents having all instances of a subject clustered in a few weeks.
        """
        # Process each group and subject separately
        for group_name, subjects in self.variables.items():
            for subject_name, subject_courses in subjects.items():
                # Skip subjects with too few courses
                if len(subject_courses) < 2:
                    continue
                    
                # Debug
                #print(f"\nBalancing {subject_name} for {group_name} with {len(subject_courses)} courses")
                
                # Get all course variables for this subject
                courses = list(subject_courses.values())
                
                # Calculate weeks in the schedule
                timeslots_per_week = 7 * len(self.university.time_ranges)
                num_weeks = len(self.university.timeslots) // timeslots_per_week
                
                # Skip if there's only one week
                if num_weeks <= 1:
                    continue
                    
                total_courses = len(courses)
                target_courses_per_week = total_courses / num_weeks
                
                # Debug
                #print(f"Target courses per week: {target_courses_per_week}")
                
                # Count courses per week
                week_counts = []
                for week in range(num_weeks):
                    # Create course counter for this week
                    week_courses = self.model.NewIntVar(0, len(courses), f'week_count_{group_name}_{subject_name}_{week}')
                    week_start = week * timeslots_per_week
                    week_end = week_start + timeslots_per_week
                    
                    # Count how many courses are in this week
                    course_indicators = []
                    for course in courses:
                        is_in_week = self.model.NewBoolVar(f'course_in_week_{group_name}_{subject_name}_{week}_{id(course)}')
                        self.model.Add(course['timeslot'] >= week_start).OnlyEnforceIf(is_in_week)
                        self.model.Add(course['timeslot'] < week_end).OnlyEnforceIf(is_in_week)
                        course_indicators.append(is_in_week)
                    
                    self.model.Add(week_courses == sum(course_indicators))
                    week_counts.append(week_courses)
                
                # Add soft constraints to keep counts near the target
                target = int(target_courses_per_week) if target_courses_per_week >= 1 else 1
                for week_idx, week_count in enumerate(week_counts):
                    # Create variables for above and below target
                    above_target = self.model.NewIntVar(0, len(courses), f'subj_above_target_{group_name}_{subject_name}_{week_idx}')
                    below_target = self.model.NewIntVar(0, len(courses), f'subj_below_target_{group_name}_{subject_name}_{week_idx}')
                    
                    # Link them to the actual count
                    self.model.Add(week_count - target == above_target - below_target)
                    
                    # Add both to penalties with higher weight than general balance
                    self.balance_penalties.append(above_target * 2)  # Higher weight
                    self.balance_penalties.append(below_target * 2)  # Higher weight

    def minimizeGaps(self):
        """
        Add soft constraints to minimize gaps in daily schedules for each group.
        A gap is defined as one or more consecutive empty timeslots between scheduled courses on the same day,
        EXCLUDING lunch break timeslots which are intended to be free.
        Each day is treated separately - gaps don't span across days.
        """
        # Number of timeslots per day
        slots_per_day = len(self.university.time_ranges)
        
        # Define the lunch break timeslot index within a day (11:45 -> 13:15), where slot index % slots_per_day == 2
        lunch_break_offset = 2  # Slot offset for lunch within a day
        
        # Process each group separately
        for group_name, subjects in self.variables.items():
            # Get all courses for this group
            group_courses = []
            for subject_courses in subjects.values():
                group_courses.extend(subject_courses.values())
            
            # Calculate the number of days in the schedule
            num_days = len(self.university.timeslots) // slots_per_day
            
            # For each day, create a binary variable for each slot indicating if it's used
            for day in range(num_days):
                day_start = day * slots_per_day
                
                # Array of boolean variables indicating if each slot is used
                slot_used = []
                for slot_offset in range(slots_per_day):
                    absolute_slot = day_start + slot_offset
                    is_used = self.model.NewBoolVar(f'slot_used_{group_name}_{day}_{slot_offset}')
                    
                    # Check if this slot is used by any course
                    slot_course_indicators = []
                    for course in group_courses:
                        in_slot = self.model.NewBoolVar(f'in_slot_{group_name}_{day}_{slot_offset}_{id(course)}')
                        self.model.Add(course['timeslot'] == absolute_slot).OnlyEnforceIf(in_slot)
                        self.model.Add(course['timeslot'] != absolute_slot).OnlyEnforceIf(in_slot.Not())
                        slot_course_indicators.append(in_slot)
                    
                    if slot_course_indicators:
                        self.model.AddBoolOr(slot_course_indicators).OnlyEnforceIf(is_used)
                        self.model.AddBoolAnd([ind.Not() for ind in slot_course_indicators]).OnlyEnforceIf(is_used.Not())
                    else:
                        self.model.Add(is_used == 0)
                    
                    slot_used.append(is_used)
                
                # Now check for gaps in this day's schedule
                gap_indicators = []
                
                # Skip the lunch break slot in our gap check
                non_lunch_slots = [i for i in range(slots_per_day) if i != lunch_break_offset]
                
                # Find the first and last used slots of the day (excluding lunch)
                first_used_slot = None
                last_used_slot = None
                
                for i in non_lunch_slots:
                    # Check if this is potentially the first used slot
                    is_first = self.model.NewBoolVar(f'is_first_{group_name}_{day}_{i}')
                    
                    # This slot must be used to be first
                    self.model.Add(slot_used[i] == 1).OnlyEnforceIf(is_first)
                    
                    # All slots before this must be unused
                    before_unused = []
                    for j in non_lunch_slots:
                        if j < i:
                            before_unused.append(slot_used[j].Not())
                    
                    if before_unused:
                        self.model.AddBoolAnd(before_unused).OnlyEnforceIf(is_first)
                        self.model.AddBoolOr([slot_used[i].Not()] + [slot_used[j] for j in non_lunch_slots if j < i]).OnlyEnforceIf(is_first.Not())
                    else:
                        # If there are no slots before, then this is the first slot if it's used
                        self.model.Add(is_first == slot_used[i])
                    
                    # Similarly for the last used slot
                    is_last = self.model.NewBoolVar(f'is_last_{group_name}_{day}_{i}')
                    
                    # This slot must be used to be last
                    self.model.Add(slot_used[i] == 1).OnlyEnforceIf(is_last)
                    
                    # All slots after this must be unused
                    after_unused = []
                    for j in non_lunch_slots:
                        if j > i:
                            after_unused.append(slot_used[j].Not())
                    
                    if after_unused:
                        self.model.AddBoolAnd(after_unused).OnlyEnforceIf(is_last)
                        self.model.AddBoolOr([slot_used[i].Not()] + [slot_used[j] for j in non_lunch_slots if j > i]).OnlyEnforceIf(is_last.Not())
                    else:
                        # If there are no slots after, then this is the last slot if it's used
                        self.model.Add(is_last == slot_used[i])
                    
                    # Store these variables for later use
                    if first_used_slot is None:
                        first_used_slot = is_first
                    if last_used_slot is None:
                        last_used_slot = is_last
                
                # Now check for each potential gap between first and last used slots
                for i in range(len(non_lunch_slots) - 2):
                    curr_idx = non_lunch_slots[i]
                    next_idx = non_lunch_slots[i + 1]
                    # Skip if next slot is not consecutive (lunch break in between)
                    if next_idx != curr_idx + 1:
                        continue
                    
                    # Check if we have a transition from used to unused
                    gap_start = self.model.NewBoolVar(f'gap_start_{group_name}_{day}_{curr_idx}')
                    self.model.AddBoolAnd([slot_used[curr_idx], slot_used[next_idx].Not()]).OnlyEnforceIf(gap_start)
                    self.model.AddBoolOr([slot_used[curr_idx].Not(), slot_used[next_idx]]).OnlyEnforceIf(gap_start.Not())
                    
                    # Find where the gap ends (transition from unused to used)
                    for j in range(i + 1, len(non_lunch_slots) - 1):
                        gap_end_idx = non_lunch_slots[j]
                        gap_next_idx = non_lunch_slots[j + 1]
                        # Skip if next slot is not consecutive
                        if gap_next_idx != gap_end_idx + 1:
                            continue
                        
                        gap_end = self.model.NewBoolVar(f'gap_end_{group_name}_{day}_{gap_end_idx}')
                        self.model.AddBoolAnd([slot_used[gap_end_idx].Not(), slot_used[gap_next_idx]]).OnlyEnforceIf(gap_end)
                        self.model.AddBoolOr([slot_used[gap_end_idx], slot_used[gap_next_idx].Not()]).OnlyEnforceIf(gap_end.Not())
                        
                        # If both gap_start and gap_end are true, we have a gap
                        is_gap = self.model.NewBoolVar(f'is_gap_{group_name}_{day}_{curr_idx}_{gap_end_idx}')
                        self.model.AddBoolAnd([gap_start, gap_end]).OnlyEnforceIf(is_gap)
                        self.model.AddBoolOr([gap_start.Not(), gap_end.Not()]).OnlyEnforceIf(is_gap.Not())
                        
                        # Calculate gap size (number of empty slots)
                        gap_size = gap_end_idx - curr_idx
                        
                        # Apply a weighted penalty based on gap size
                        weighted_penalty = self.model.NewIntVar(0, 3 * gap_size, f'weighted_gap_{group_name}_{day}_{curr_idx}_{gap_end_idx}')
                        self.model.Add(weighted_penalty == 3 * gap_size).OnlyEnforceIf(is_gap)
                        self.model.Add(weighted_penalty == 0).OnlyEnforceIf(is_gap.Not())
                        
                        self.gap_penalties.append(weighted_penalty)

    def minimize_campus_returns(self):
        """
        Add soft constraints to minimize transitions between online and in-person classes.
        For each group, penalize schedules where students have to switch between physical and
        online classes within the same day.
        """
        # Identify the index of the "online" room
        online_room_index = None
        for i, room in enumerate(self.university.rooms):
            if room.name.lower() == "online":
                online_room_index = i
                break
        
        # If there's no online room, this constraint doesn't apply
        if online_room_index is None:
            print(" - - No online room found, skipping online transition minimization")
            return
        
        print(" - - Adding online-to-physical transition penalties...")
        
        # Number of timeslots per day
        slots_per_day = len(self.university.time_ranges)
        
        group_counter = 0
        # Process each group separately
        for group_name, subjects in self.variables.items():
            group_counter += 1
            # Get all courses for this group
            group_courses = []
            for subject_courses in subjects.values():
                group_courses.extend(subject_courses.values())
            
            # Calculate the number of days in the schedule
            num_days = len(self.university.timeslots) // slots_per_day
            
            # For each day, check for transitions
            for day in range(num_days):
                print(f" - - Group {group_counter}, day {day+1}/{num_days}              ", end="\r")

                day_start = day * slots_per_day
                day_end = day_start + slots_per_day
                
                # Create variables for each timeslot indicating if it has an online course
                is_online_slot = []
                is_physical_slot = []
                
                for slot_offset in range(slots_per_day):
                    absolute_slot = day_start + slot_offset
                    
                    # Variable for if this slot has an online course
                    has_online = self.model.NewBoolVar(f'has_online_{group_name}_{day}_{slot_offset}')
                    has_physical = self.model.NewBoolVar(f'has_physical_{group_name}_{day}_{slot_offset}')
                    
                    # Indicators for each course in this slot
                    online_indicators = []
                    physical_indicators = []
                    
                    for course in group_courses:
                        in_slot = self.model.NewBoolVar(f'in_slot_{group_name}_{day}_{slot_offset}_{id(course)}')
                        self.model.Add(course['timeslot'] == absolute_slot).OnlyEnforceIf(in_slot)
                        self.model.Add(course['timeslot'] != absolute_slot).OnlyEnforceIf(in_slot.Not())
                        
                        # Check if course is online
                        is_online = self.model.NewBoolVar(f'is_online_{group_name}_{day}_{slot_offset}_{id(course)}')
                        self.model.Add(course['room'] == online_room_index).OnlyEnforceIf(is_online)
                        self.model.Add(course['room'] != online_room_index).OnlyEnforceIf(is_online.Not())
                        
                        # Link the two conditions
                        is_online_course = self.model.NewBoolVar(f'is_online_course_{group_name}_{day}_{slot_offset}_{id(course)}')
                        self.model.AddBoolAnd([in_slot, is_online]).OnlyEnforceIf(is_online_course)
                        self.model.AddBoolOr([in_slot.Not(), is_online.Not()]).OnlyEnforceIf(is_online_course.Not())
                        
                        is_physical_course = self.model.NewBoolVar(f'is_physical_course_{group_name}_{day}_{slot_offset}_{id(course)}')
                        self.model.AddBoolAnd([in_slot, is_online.Not()]).OnlyEnforceIf(is_physical_course)
                        self.model.AddBoolOr([in_slot.Not(), is_online]).OnlyEnforceIf(is_physical_course.Not())
                        
                        online_indicators.append(is_online_course)
                        physical_indicators.append(is_physical_course)
                    
                    # Mark slot as having online course if any course is online
                    if online_indicators:
                        self.model.AddBoolOr(online_indicators).OnlyEnforceIf(has_online)
                        self.model.AddBoolAnd([ind.Not() for ind in online_indicators]).OnlyEnforceIf(has_online.Not())
                    else:
                        self.model.Add(has_online == 0)
                    
                    # Mark slot as having physical course if any course is physical
                    if physical_indicators:
                        self.model.AddBoolOr(physical_indicators).OnlyEnforceIf(has_physical)
                        self.model.AddBoolAnd([ind.Not() for ind in physical_indicators]).OnlyEnforceIf(has_physical.Not())
                    else:
                        self.model.Add(has_physical == 0)
                    
                    is_online_slot.append(has_online)
                    is_physical_slot.append(has_physical)
                
                # Now detect transitions between consecutive slots
                for i in range(slots_per_day - 1):
                    # Transition from online to physical
                    online_to_physical = self.model.NewBoolVar(f'online_to_physical_{group_name}_{day}_{i}')
                    self.model.AddBoolAnd([is_online_slot[i], is_physical_slot[i+1]]).OnlyEnforceIf(online_to_physical)
                    self.model.AddBoolOr([is_online_slot[i].Not(), is_physical_slot[i+1].Not()]).OnlyEnforceIf(online_to_physical.Not())
                    
                    # Transition from physical to online  
                    physical_to_online = self.model.NewBoolVar(f'physical_to_online_{group_name}_{day}_{i}')
                    self.model.AddBoolAnd([is_physical_slot[i], is_online_slot[i+1]]).OnlyEnforceIf(physical_to_online)
                    self.model.AddBoolOr([is_physical_slot[i].Not(), is_online_slot[i+1].Not()]).OnlyEnforceIf(physical_to_online.Not())
                    
                    # Add penalty for each transition
                    # High penalty weight (10) to prioritize this constraint
                    transition_penalty = self.model.NewIntVar(0, 10, f'transition_penalty_{group_name}_{day}_{i}')
                    self.model.Add(transition_penalty == 10).OnlyEnforceIf(online_to_physical)
                    self.model.Add(transition_penalty == 10).OnlyEnforceIf(physical_to_online)
                    self.model.Add(transition_penalty == 0).OnlyEnforceIf(online_to_physical.Not())
                    self.model.Add(transition_penalty == 0).OnlyEnforceIf(physical_to_online.Not())
                    
                    # Add to balance penalties list
                    self.balance_penalties.append(transition_penalty)
        print("")

    def minimize_late_slots(self):
        """
        Add soft constraints to discourage scheduling courses in the last two timeslots
        of each day. This helps create more favorable schedules for students and teachers.
        """
        print(" - - Adding penalties for late timeslots...")
        
        # Number of timeslots per day
        slots_per_day = len(self.university.time_ranges)
        
        # Identify the last two timeslots of each day (indexes for each day)
        late_slot_offsets = [slots_per_day - 2, slots_per_day - 1]
        
        # Get all courses
        all_courses = []
        for group_subjects in self.variables.values():
            for subject_courses in group_subjects.values():
                all_courses.extend(subject_courses.values())
        
        # Calculate the number of days in the schedule
        num_days = len(self.university.timeslots) // slots_per_day
        
        # For each course, check if it's in a late slot
        for course in all_courses:
            timeslot_var = course['timeslot']
            
            # Create a variable to track if this course is in a late slot
            is_late_slot = self.model.NewBoolVar(f'is_late_slot_{id(course)}')
            
            # Create indicators for each possible late slot
            late_indicators = []
            for day in range(num_days):
                for offset in late_slot_offsets:
                    slot_idx = day * slots_per_day + offset
                    
                    # Course is in this late slot
                    in_this_slot = self.model.NewBoolVar(f'in_late_slot_{day}_{offset}_{id(course)}')
                    self.model.Add(timeslot_var == slot_idx).OnlyEnforceIf(in_this_slot)
                    self.model.Add(timeslot_var != slot_idx).OnlyEnforceIf(in_this_slot.Not())
                    
                    late_indicators.append(in_this_slot)
            
            # Course is in a late slot if it's in any of the identified late slots
            if late_indicators:
                self.model.AddBoolOr(late_indicators).OnlyEnforceIf(is_late_slot)
                self.model.AddBoolAnd([ind.Not() for ind in late_indicators]).OnlyEnforceIf(is_late_slot.Not())
                
                # Apply penalty for late slots
                # Use weight of 8 - significant but less than campus returns (15) or room conflicts
                late_penalty = self.model.NewIntVar(0, 8, f'late_slot_penalty_{id(course)}')
                self.model.Add(late_penalty == 8).OnlyEnforceIf(is_late_slot)
                self.model.Add(late_penalty == 0).OnlyEnforceIf(is_late_slot.Not())
                
                # Add to balance penalties
                self.balance_penalties.append(late_penalty)

    def solveCSP(self):
        """Enhanced solve method with comprehensive conflict tracking and objective value monitoring."""
        start_time = time.time()

        # Configure solver for flexibility
        import multiprocessing
        if int(multiprocessing.cpu_count()) >= 4:
            worknum = 4
        else:
            worknum = multiprocessing.cpu_count()/2
        self.solver.parameters.num_search_workers = worknum
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
        self.chronometer = ChronometerCallback(
            self.model, 
            self.conflict_penalties, 
            self.balance_penalties, 
            self.gap_penalties, 
            self.test
        )
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
                # Add penalty breakdown analysis
                schedule_intel.analyze_penalty_breakdown(self.solver, self)
            except Exception as e:
                print(f"Error in schedule intelligence analysis: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No complete solution found. Please retry giving the CSP more time !")
            print("If time limit wasn't reached, this might mean that the instance is inconsistent and that no solution can be found !")
            print(" -> You may want to modify the instance of your problem (adding more days...)")
        
        print(f"\nComputational time: {round((time.time()-start_time),3)} s")
        self.append_to_report(f"\n\n\nComputational time: {round((time.time()-start_time),3)} s")
        print(f"Best objective value: {self.chronometer.best_objective}")
        self.append_to_report(f"\nBest objective value: {self.chronometer.best_objective}")
        print(f"Total solutions found: {self.chronometer.solution_count}")
        self.append_to_report(f"\nTotal solutions found: {self.chronometer.solution_count}")

        return self.generated_courses