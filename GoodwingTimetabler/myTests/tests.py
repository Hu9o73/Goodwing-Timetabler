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

    # Organize courses by group
    for course in csp_solver.generated_courses:
        if course.group.name not in group_courses:
            group_courses[course.group.name] = []
        group_courses[course.group.name].append(course)

    # Output each group's schedule
    for group_name, courses in group_courses.items():
        outputSchedule(courses, group_name)

# Utility to output a schedule for a single group
def outputSchedule(courses: List[Course], groupName: str):
    print(f"Outputting schedule for group {groupName}")
    util.append_courses_to_yaml_file(courses, f'./Outputs/yml/{groupName}.yml')
    os.system(f'pdfschedule --start-monday --font-size 8 ./Outputs/yml/{groupName}.yml ./Outputs/pdf/{groupName}.pdf')