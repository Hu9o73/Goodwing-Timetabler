from csp import *
import util
import os
import datetime as dt


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




def generateCoursesForUniv(my_univ: University) -> List[Course]:
    courses: List[Course] = []

    # Courses for A1 TDA
    courses.append(Course(my_univ.timeslots[0], my_univ.promotions[0].groups[0], my_univ.promotions[0].subjects[0], my_univ.teachers[0], my_univ.rooms[0]))
    courses.append(Course(my_univ.timeslots[1], my_univ.promotions[0].groups[0], my_univ.promotions[0].subjects[1], my_univ.teachers[3], my_univ.rooms[2]))
    courses.append(Course(my_univ.timeslots[3], my_univ.promotions[0].groups[0], my_univ.promotions[0].subjects[2], my_univ.teachers[6], my_univ.rooms[3]))
    courses.append(Course(my_univ.timeslots[4], my_univ.promotions[0].groups[0], my_univ.promotions[0].subjects[2], my_univ.teachers[6], my_univ.rooms[3]))

    # Courses for A2 TDB
    courses.append(Course(my_univ.timeslots[1], my_univ.promotions[1].groups[1], my_univ.promotions[1].subjects[1], my_univ.teachers[4], my_univ.rooms[1]))
    courses.append(Course(my_univ.timeslots[3], my_univ.promotions[1].groups[1], my_univ.promotions[1].subjects[2], my_univ.teachers[5], my_univ.rooms[1]))
    courses.append(Course(my_univ.timeslots[4], my_univ.promotions[1].groups[1], my_univ.promotions[1].subjects[0], my_univ.teachers[1], my_univ.rooms[4]))
    courses.append(Course(my_univ.timeslots[5], my_univ.promotions[1].groups[1], my_univ.promotions[1].subjects[0], my_univ.teachers[1], my_univ.rooms[4]))

    outputSchedule(courses, "A1_TDA")
    outputSchedule(courses, "A2_TDB")

    return courses




def outputSchedule(courses: List[Course], groupName: str):
    print("Outputting schedule for group ", groupName)
    groupCourse: List[Course] = []
    for course in courses:
        if course.group.name == groupName:
            groupCourse.append(course)

    util.append_courses_to_yaml_file(groupCourse, f'./Outputs/yml/{groupName}.yml')
    os.system(f'pdfschedule --start-monday --font-size 8 ./Outputs/yml/{groupName}.yml ./Outputs/pdf/{groupName}.pdf')




def generateMockCSP():
    print("generateMockCSP() running...\n")
    my_univ = generateUniv("ESILV", dt.date(2025, 1, 6), 7, time_ranges)

    courses = generateCoursesForUniv(my_univ)

    constraintsValidated = checkConstraints(my_univ, courses)
    print("Constraints validation: ", constraintsValidated)