#
# Imports
#

import datetime as dt
from typing import List

#
#   Basic objects (to build complex ones)
#   These classes don't rely on any other(s) to be instanciated
#

class Timeslot:
    """
    Object representing a timeslot.\n
    Parameters:\n
    - day : datetime.date | Date of the timeslot
    - start : datetime.time | Start date and time of the timeslot
    - end: datetime.time | End date and time of the timeslot
    """
    def __init__(self, day: dt.date, start: dt.time, end: dt.time):
        self.day = day
        self.start = start
        self.end = end

    def __str__(self):
        return f"Timeslot date: {self.date} , starts at: {self.start} , ends at: {self.end}"


class Person:
    """
    Object for any person (teacher, student, etc...)\n
    Parameters:\n
    - first_name: str | First name of the person
    - last_name: str | Last name of the person
    """
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subject:
    """
    Object representing a school subject.\n
    Parameters:\n
    - name : str | The name of the subject
    - id : str | The id of the subject (if applicable, '0' by default)
    - hours : float | The number of hours to complete the course (9.0 by default)
    """
    def __init__(self, name: str, id: str = "0", hours: float = 9.0):
        self.name = name
        self.id = id
        self.hours = hours

    def __str__(self):
        return f"{self.name} with id: {self.id}"


#
#   People
#

class Teacher(Person):
    """
    Object representing a teacher.\n
    Parameters:\n
    - subjects : [Subject] | List of the subjects the teacher is able to teach
    """
    def __init__(self, first_name: str, last_name: str, subjects: List[Subject] = []):
        super().__init__(first_name, last_name)
        self.subjects = subjects

    def __str__(self):
        result = super().__str__() + " can teach: ["
        for subject in self.subjects:
            result += subject.name + " "
        result += "]"
        return result

class Student(Person):
    """
    Object representing a student.\n
    Parameters:\n
    - student_id : str | Badge id of the student (Default : '0')
    """
    def __init__(self, first_name: str, last_name: str, student_id: str = "0"):
        super().__init__(first_name, last_name)
        self.student_id = student_id

    def __str__(self):
        return f"{super().__str__} is a student with id: {self.student_id}"


#
#   Facilities
#

class Room:
    """
    Object representing a room, used by the university.\n
    Parameters:\n
    - name : str | Name of the room.
    - type : str | Type of the room if it's a special room. Otherwise "default"
    """
    def __init__(self, name: str, type: str = "default"):
        self.name = name
        self.type = type

    def __str__(self):
        return f"Room {self.name} has type: {self.type}"


#
#   Scholarship
#

class Group:
    """
    Object representing a class (in the 'group of students' meaning)\n
    Parameters:\n
    - name : str | The name of the group
    - students : [Student] | List of the students in the class, None by default
    """
    def __init__(self, name: str, students: List[Student] = None):
        self.name = name
        self.students = students

    def __str__(self):
        return f"{self.name}"
    
class Promotion:
    """
    Object representing a promotion (multiple groups on the same level)\n
    Parameters:\n
    - name : str | Name of the promotion
    - groups : [Group] | List of the groups on this promotion
    - subjects : [Subject] | List of the subjects the promotion has to attend
    """
    def __init__(self, name: str, groups: List[Group], subjects: List[Subject]):
        self.name = name
        self.groups = groups
        self.subjects = subjects

    def __str__(self):
        groupCount = len(self.groups)
        subjectsCount = len(self.subjects)
        return f"Promotion {self.name} has {groupCount} groups and must attend {subjectsCount} subjects."


#
#   Complex end objects
#

class Course:
    """
    Object representing the courses.\n
    Prameters:\n
    - timeslot : Timeslot | The Timeslot the course takes place on
    - group : Group | The group attending the course
    - subject : Subject | The subject the course is about
    - teacher : Teacher | The teacher giving the course
    """
    def __init__(self, timeslot: Timeslot, group: Group, subject: Subject, teacher: Teacher, room: Room):
        self.timeslot = timeslot
        self.group = group
        self.subject = subject
        self.teacher = teacher
        self.room = room


class University:
    """
    Object representing a university.\n
    Parameters:\n
    - name : str | University's name
    - rooms : [Room] | List of rooms in our university.
    - teachers: [Teacher] | List of teachers in the university.
    - promotions: [Promotion] | List of promotions in the university.
    """
    def __init__(self, name: str, rooms: List[Room], teachers: List[Teacher], promotions: List[Promotion]):
        self.name = name
        self.rooms = rooms
        self.teachers = teachers
        self.promotions = promotions

    def __str__(self):
        return f"{self.name} has {len(self.rooms)} rooms, {len(self.teachers)} teachers and {len(self.promotions)} promotions."