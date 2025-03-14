# File to instantiate a university and a schedule with courses
from .objects import *
import pandas as pd
import numpy as np
from collections import defaultdict

def generateUniv2(gen_dir:str = './GoodwingTimetabler/UniversityInstance/'):
    from util import createCSV
    createCSV(gen_dir)

    # Getting the general info
    uniCSV = pd.read_csv(gen_dir+'csv/University.csv', sep=',')
    name = uniCSV["Value"][0]
    start_date = dt.date(int(uniCSV["Value"][3]), int(uniCSV["Value"][2]), int(uniCSV["Value"][1]))
    days = int(uniCSV["Value"][4])

    # Getting the values for the rooms
    roomsCSV = pd.read_csv(gen_dir+'csv/Rooms.csv', sep=',')
    rooms = []
    for _, row in roomsCSV.iterrows():
        rooms.append(Room(row["Name"], row["Type"]))

    # Getting the values for the subjects
    subjectsCSV = pd.read_csv(gen_dir + 'csv/Subjects.csv', sep=',')
    subjects = []
    for idx, row in subjectsCSV.iterrows():
        subjects.append([row["Id"], row["Promotion"], Subject(row["Name"], row["Id"], row["Hours"], row["Color"])])
    
    promotion_dict = defaultdict(list)                  # Dictionary to group subjects by promotion
    for uni, promotion, subject in subjects:            # Populate dictionary
        promotion_dict[promotion].append(subject)
    ordered_subjects = list(promotion_dict.values())    # Convert dictionary values to a list of lists


    # Getting the values for the promotions
    promotionsCSV = pd.read_csv(gen_dir+'csv/Promotions.csv', sep=',')
    groups_names = []
    promo_names = []
    for col in promotionsCSV.columns:
        non_null_values = promotionsCSV[col].dropna().tolist()  # Remove NaN values
        if non_null_values:  # Only add if there are valid values
            groups_names.append([col + '_' + val for val in non_null_values])
            promo_names.append(col)

    groups = []

    # Creating groups from filtered data
    for promo in groups_names:
        group_list = [Group(group_name) for group_name in promo]  # Create only valid groups
        groups.append(group_list)

    promotions = []
    for idx, promo_name in enumerate(promo_names):
        promotions.append(Promotion(promo_name, groups[idx], ordered_subjects[idx]))


    def get_subject_by_id(data: pd.DataFrame, target_id: str) -> Subject:
        for subject in data:
            if subject[0] == target_id:
                return subject[2]
        return None   

    # Getting the timeslots
    timeslotsCSV = pd.read_csv(gen_dir + 'csv/Timeslots.csv')
    time_ranges = []
    for idx, row in timeslotsCSV.iterrows():
        time_ranges.append((dt.time(row["StartH"], row["StartMin"]), dt.time(row["EndH"], row["EndMin"])))
    
    slots_per_day = len(time_ranges)
    
    # Getting the values for the teachers
    teachersCSV = pd.read_csv(gen_dir + 'csv/Teachers.csv', sep=',')
    
    # Try to get teacher availability data
    try:
        availabilityCSV = pd.read_csv(gen_dir + 'csv/TeacherAvailability.csv', sep=',')
        has_availability_data = True
        
        # Create a lookup dictionary for teacher availability by ID
        teacher_availability_dict = {}
        
        for _, row in availabilityCSV.iterrows():
            teacher_id = str(row['TeacherId'])
            
            # Skip header rows or rows without teacher ID
            if teacher_id == 'TeacherId' or pd.isna(teacher_id):
                continue
                
            # Initialize availability matrix (7 days x slots_per_day)
            availability_matrix = np.zeros((7, slots_per_day), dtype=int)
            
            # Process each day
            days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            for day_idx, day in enumerate(days_of_week):
                for slot_idx in range(slots_per_day):
                    # Column name format: Day_StartTime-EndTime (e.g. Mon_8:15-9:45)
                    # Fix for the str attribute error - directly format integers as strings without using pandas methods
                    start_hour = str(int(timeslotsCSV["StartH"].iloc[slot_idx]))
                    start_min = str(int(timeslotsCSV["StartMin"].iloc[slot_idx])).zfill(2)
                    end_hour = str(int(timeslotsCSV["EndH"].iloc[slot_idx]))
                    end_min = str(int(timeslotsCSV["EndMin"].iloc[slot_idx])).zfill(2)
                    
                    col_name = f"{day}_{start_hour}:{start_min}-{end_hour}:{end_min}"
                    
                    # Check if column exists and value is available (1)
                    if col_name in row.index and row[col_name] == 1:
                        availability_matrix[day_idx][slot_idx] = 1
            
            # Convert weekly matrix to full schedule slot list
            available_slots = []
            
            # Calculate number of weeks needed for the full period
            num_weeks = (days + 6) // 7
            
            for week in range(num_weeks):
                for day in range(7):
                    actual_day = week * 7 + day
                    if actual_day >= days:  # Skip days beyond the specified period
                        break
                    
                    for slot in range(slots_per_day):
                        if availability_matrix[day][slot] == 1:
                            # Calculate absolute slot index
                            slot_idx = actual_day * slots_per_day + slot
                            available_slots.append(slot_idx)
            
            teacher_availability_dict[teacher_id] = available_slots
                
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("No teacher availability data found. All teachers will be considered available for all slots.")
        has_availability_data = False
    except Exception as e:
        print(f"Error processing teacher availability: {e}")
        print("All teachers will be considered available for all slots.")
        has_availability_data = False
    
    # Process teachers
    teachers = []
    for idx, row in teachersCSV.iterrows():
        teacher_id = str(row["Idt"])
        teacher_subjects_id = row["Subjects (séparés d'un '-')"].split('-')
        teacher_subjects = []
        for id in teacher_subjects_id:
            teacher_subjects.append(get_subject_by_id(subjects, id))
        
        # Set teacher availability
        if has_availability_data and teacher_id in teacher_availability_dict:
            teacher_availability = teacher_availability_dict[teacher_id]
        else:
            # Default: available for all slots
            teacher_availability = [i for i in range(days * slots_per_day)]
        
        teachers.append(Teacher(row["First Name"], row["Last Name"], teacher_subjects, teacher_availability))

    my_univ = University(name, rooms, teachers, promotions, start_date, days, time_ranges)

    return my_univ
        
    




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


