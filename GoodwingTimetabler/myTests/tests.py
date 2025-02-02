from csp import *
import util
import os
import datetime as dt

def generateScheduleUsingCSP():
    print("generateScheduleUsingCSP() running...\n")

    # Create the university
    my_univ = generateUniv("ESILV", dt.date(2025, 1, 6), 7, time_ranges)

    # Instantiate and solve the CSP
    scheduler = CSP(my_univ)

    # Output the generated schedules
    outputSchedulesFromCSP(scheduler)


def outputSchedulesFromCSP(csp_solver: CSP):
    group_courses = {}

    print("\nDEBUG: Initial courses from CSP:")
    for course in csp_solver.generated_courses:
        print(f"Subject: {course.subject.name}, Day: {course.timeslot.day}, Time: {course.timeslot.start}-{course.timeslot.end}")

    # Organize courses by group
    for course in csp_solver.generated_courses:
        if course.group.name not in group_courses:
            group_courses[course.group.name] = []
        group_courses[course.group.name].append(course)

    print("\nDEBUG: Courses after grouping:")
    for group_name, courses in group_courses.items():
        print(f"\nGroup: {group_name}")
        for course in courses:
            print(f"Subject: {course.subject.name}, Day: {course.timeslot.day}, Time: {course.timeslot.start}-{course.timeslot.end}")

    # Output each group's schedule
    for group_name, courses in group_courses.items():
        outputSchedule(courses, group_name)

# Utility to output a schedule for a single group
def outputSchedule(courses: List[Course], groupName: str):
    print(f"Outputting schedule for group {groupName}")
    util.append_courses_to_yaml_file(courses, f'./Outputs/yml/{groupName}.yml', groupName)
    # Note: pdf schedule is buggy
    # Schedule saved as png in the append_courses_to_yaml func (this is the one to trust !)
    # os.system(f'pdfschedule --start-monday --font-size 8 ./Outputs/yml/{groupName}.yml ./Outputs/pdf/{groupName}.pdf')