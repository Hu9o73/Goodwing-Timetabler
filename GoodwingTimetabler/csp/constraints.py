from .objects import *

def checkConstraints(univ: University, courses: List[Course]):
        if not noRoomOverlap(univ, courses):
            return False
        if not noDuplicateTeacher(univ, courses):
            return False
        if not noDuplicateGroup(univ, courses):
            return False
        if not teachersAssignedToTheirSubject(courses):
            return False
        return True

def noRoomOverlap(univ: University, courses: List[Course]):
    for timeslot in univ.timeslots:
        coursesOnCurrentTimeslot: List[Course] = []

        for course in courses:
            if course.timeslot == timeslot:
                coursesOnCurrentTimeslot.append(course)
            
        occupiedRoomsOnCurrentTimeslot: List[Room] = []
        for course in coursesOnCurrentTimeslot:
            occupiedRoomsOnCurrentTimeslot.append(course.room)

        noDuplicateRoomsOnCurrentTimeslot = set(occupiedRoomsOnCurrentTimeslot)

        if(len(noDuplicateRoomsOnCurrentTimeslot) != len(occupiedRoomsOnCurrentTimeslot)):
            print("Room overlapping on timeslot: ", timeslot)
            return False

    return True


def noDuplicateTeacher(univ: University, courses: List[Course]):
    for timeslot in univ.timeslots:
        coursesOnCurrentTimeslot: List[Course] = []
        
        for course in courses:
            if course.timeslot == timeslot:
                coursesOnCurrentTimeslot.append(course)

        teachersAssignedToCurrentTimeslot: List[Teacher] = []
        for course in coursesOnCurrentTimeslot:
            teachersAssignedToCurrentTimeslot.append(course.teacher)

        noDuplicateTeacherOnCurrentTimeslot = set(teachersAssignedToCurrentTimeslot)

        if(len(noDuplicateTeacherOnCurrentTimeslot) != len(teachersAssignedToCurrentTimeslot)):
            print("Teacher assigned twice on the same timeslot: ", timeslot)
            return False
        
    return True

def noDuplicateGroup(univ: University, courses: List[Course]):
    for timeslot in univ.timeslots:
        coursesOnCurrentTimeslot: List[Course] = []
        
        for course in courses:
            if course.timeslot == timeslot:
                coursesOnCurrentTimeslot.append(course)
        
        groupsAssignedToCurrentTimeslot: List[Group] = []
        for course in coursesOnCurrentTimeslot:
            groupsAssignedToCurrentTimeslot.append(course.group)

        noDuplicateGroupOnCurrentTimeslot = set(groupsAssignedToCurrentTimeslot)
        if(len(noDuplicateGroupOnCurrentTimeslot) != len(groupsAssignedToCurrentTimeslot)):
            print("Group assigned to 2 courses on timeslot: ", timeslot)
            return False
        
    return True

def teachersAssignedToTheirSubject(courses: List[Course]):
    for course in courses:
        if course.subject not in course.teacher.subjects:
            print(f"{course.teacher.first_name} {course.teacher.last_name} assigned to {course.subject} but can only teach {', '.join(sub.name for sub in course.teacher.subjects)} | Group: {course.group.name} | Timeslot: {course.timeslot}")
            return False
        
    return True