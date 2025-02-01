# File to instantiate a university and a schedule with courses

from .objects import *

def generateUniv(name: str, start_date: dt.date, days: int, timeslots: List[tuple]):
    """
    Generates a mock university with the given name.
    """

    #
    #   Subjects instantiation
    #

    s1 = Subject("Basic Maths", "UNI011", 6.0, "0c0fcc")
    s2 = Subject("Basic Physics", "UNI012", 9.0, "9008d4")
    s3 = Subject("Basic Informatics", "UNI013", 6.0, "05e6de")
    s4 = Subject("Advanced Maths", "UNI012", 6.0, "0a0ca3")
    s5 = Subject("Advanced Physics", "UNI022", 9.0, "55047d")
    s6 = Subject("Advanced Informatics", "UNI032", 12.0, "07b3ac")

    A1_subjects = [s1, s2, s3]
    A2_subjects = [s4, s5, s6]


    #
    #   People creation (only teachers required)
    #

    maths = [s1, s4]
    physics = [s2, s5]
    informatics = [s3, s6]

    t1_available = [0, 3, 7, 8, 10, 14, 17, 21, 24, 28, 31, 35, 38, 42]
    t2_available = [1, 4, 5, 9, 13, 16, 20, 23, 27, 30, 34, 37, 41, 43]
    t3_available = [2, 6, 11, 15, 19, 22, 26, 29, 33, 36, 40, 44]
    t4_available = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44]
    t5_available = [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41]
    t6_available = [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42]
    t7_available = [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43]
    t8_available = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40]
    t1 = Teacher("Henri", "Barbeau", maths, t1_available)
    t2 = Teacher("Timothé", "Solé", maths, t2_available)
    t3 = Teacher("Renaud", "Cerfbeer", maths, t3_available)
    t4 = Teacher("Christiane", "Brunelle", physics, t4_available)
    t5 = Teacher("Constantin", "Poussin", physics, t5_available)
    t6 = Teacher("Maurice", "Vannier", informatics, t6_available)
    t7 = Teacher("Napoléon", "Matthieu", informatics, t7_available)
    t8 = Teacher("Josette", "Paquin", informatics, t8_available)

    teachers = [t1, t2, t3, t4, t5, t6, t7, t8]


    #
    #   Rooms
    #

    r1 = Room("L101")
    r2 = Room("L102")
    r3 = Room("L103")
    r4 = Room("L104")
    r5 = Room("L105")
    r6 = Room("AmphiC", "Amphitheatre")

    rooms = [r1, r2, r3, r4, r5, r6]


    #
    #   Groups
    #

    g1 = Group("A1_TDA")
    #g2 = Group("A1_TDB")
    #g3 = Group("A1_TDC")
    #g4 = Group("A2_TDA")
    g5 = Group("A2_TDB")
    #g6 = Group("A3_TDC")

    A1_groups = [g1]
    A2_groups = [g5]


    #
    #   Promotion
    #

    A1 = Promotion("A1", A1_groups, A1_subjects)
    A2 = Promotion("A2", A2_groups, A2_subjects)


    #
    #   University
    #

    my_univ = University(name, rooms, teachers, [A1, A2], start_date, days, timeslots)

    return my_univ





#
#   Timeslots
#

# Plages horaire (start_time, end_time) pour chaque jour
time_ranges = [
    (dt.time(8, 15), dt.time(9, 45)),
    (dt.time(10, 0), dt.time(11, 30)),
    (dt.time(11, 45), dt.time(13, 15)),
    (dt.time(13, 30), dt.time(15, 0)),
    (dt.time(15, 15), dt.time(16, 45)),
    (dt.time(17, 0), dt.time(18, 30)),
    (dt.time(18, 45), dt.time(20, 15)),
]


