from csp import *
import util
import os

def generateMockUniversity():
    
    print("generateMockUniversity() running...\n")

    my_univ = generateUniv("ESILV")
    print(my_univ, "\n")

    print("Trying to access room with index 3: ")
    print(my_univ.rooms[3], "\n")
    print("Trying to access teacher with index 5: ")
    print(my_univ.teachers[5], "\n")
    print("Trying to access promotion with index 1: ")
    print(my_univ.promotions[1], "\n")
    print("Trying to access A2's subject list: ")
    for sub in my_univ.promotions[1].subjects:
        print(sub)


def generateCoursesForUniv(my_univ: University):
    courses: List[Course] = []
    timeslots = generate_timeslots(dt.date(2025, 1, 6), 6, time_ranges)

    subjects: List[Subject] = []
    for promo in my_univ.promotions:
        for subject in promo.subjects:
            subjects.append(subject)

    # Courses for A1 TDA
    courses.append(Course(timeslots[0], my_univ.promotions[0].groups[0], subjects[0], my_univ.teachers[0], my_univ.rooms[0]))
    courses.append(Course(timeslots[1], my_univ.promotions[0].groups[0], subjects[1], my_univ.teachers[0], my_univ.rooms[2]))
    courses.append(Course(timeslots[3], my_univ.promotions[0].groups[0], subjects[2], my_univ.teachers[0], my_univ.rooms[1]))
    courses.append(Course(timeslots[4], my_univ.promotions[0].groups[0], subjects[2], my_univ.teachers[0], my_univ.rooms[1]))

    # Courses for A2 TDB
    courses.append(Course(timeslots[1], my_univ.promotions[1].groups[1], subjects[4], my_univ.teachers[0], my_univ.rooms[1]))
    courses.append(Course(timeslots[3], my_univ.promotions[1].groups[1], subjects[5], my_univ.teachers[0], my_univ.rooms[1]))
    courses.append(Course(timeslots[4], my_univ.promotions[1].groups[1], subjects[3], my_univ.teachers[0], my_univ.rooms[4]))
    courses.append(Course(timeslots[5], my_univ.promotions[1].groups[1], subjects[3], my_univ.teachers[0], my_univ.rooms[4]))

    outputSchedule(courses, "A1_TDA")
    outputSchedule(courses, "A2_TDB")

def outputSchedule(courses: List[Course], groupName: str):
    print("Outputting schedule for group ", groupName)
    groupCourse: List[Course] = []
    for course in courses:
        if course.group.name == groupName:
            groupCourse.append(course)

    util.append_courses_to_yaml_file(groupCourse, f'./Outputs/yml/{groupName}.yml')
    os.system(f'pdfschedule --start-monday ./Outputs/yml/{groupName}.yml ./Outputs/pdf/{groupName}.pdf')

def generateMockCSP():
    print("generateMockCSP() running...\n")
    my_univ = generateUniv("ESILV")

    generateCoursesForUniv(my_univ)