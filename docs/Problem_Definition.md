# Problem Definition

*This project started as a school project. The following file talks about the problem we had to find and answer to. Nevertheless, the algorithm adapts to other university instances, not only mine ! Thus, keep in mind that course durations, timeslots, and other constraints, can be adapted to suit your needs !*

## Our problem :

### Title: Timetable Planning under New Constraints


### Description: 
The disruptions caused by the COVID-19 pandemic have introduced new constraints in managing several complex problems of daily life. 
Among these, work schedule planning, an NP-hard optimization problem, has been particularly affected. This type of problem appears in 
various sectors such as administration, transportation, production, healthcare, and education.

In this context, we focus on the problem of optimizing university timetables. Before the pandemic, creating a timetable involved 
respecting certain constraints, such as the availability of teachers, classrooms, and permissible time slots. 
Any solution meeting these constraints was considered optimal. However, new constraints have emerged with the pandemic, such as limiting the number of students physically present, distance learning, hybrid formats, making the planning process more complex.

The objective of this project is to propose solutions, either exact or approximate, for the problem of course 
scheduling by considering both classical constraints (availability of teachers and classrooms) and new constraints related 
to teaching methods (in-person, distance, or hybrid), as well as balancing the workload for students according to these modalities.

The student will begin by conducting a literature review on the problem and then develop a new solution approach. 
Finally, tests will be conducted on a dataset to evaluate the solution and test its robustness.


## Objective
The goal is to generate a timetable that minimizes the overall scheduling conflicts while satisfying the above constraints. The solution should also optimize resource utilization (rooms, teachers) and balance the workload across all stakeholders (teachers and students).


## Problem Definition:

- Our university has:
    - A given **r** number of rooms. Each room might be a **special room**.
        - **Special rooms** are rooms with specific furnitures. For instance lab furnitures are in **lab** rooms. **Lab** rooms are considered as a **special room**.
        - Rooms that aren't **special rooms** are refered too as **rooms**.
        - **Amphitheatres** are considered as **special rooms**.
    - A given **t** amount of teachers. Each teacher has one or more corresponding subjects he/she can teach.
    - **N** promotions (= year the student is on).
    Each promotion has:
        - **n** classes (= group of students)
        To each class, we assign:
            - **s** subjects (= materials) the class has to attend.
              
- Each of the **s** subjects has:
    - A fixed number of hours **h** to be completed.
    - The **h** hours are divided in **online_hours** and **presential_hours**.
    - We need to make sure that **online_hours** <= (30%) * **h**
      
- To complete the **h** hours:
    - One course duration is 1h30.
    - A class can attend as many **courses** as required to attend the **h** hours.
    - Some **courses** need to take place in special rooms depending on the **course**'s format. (For example practical works need to be in labs)
    - Two different classes can't attend the same **course** in the same **room** on the same **timeslot**
        - An exception is made for **courses** taking place in **amphitheatres**
    - One class can't have two **courses** in the same **timeslot**
      
- The **courses** can take place in defined **timeslots** each day.
    - **Timeslots** are defined as follows:
        - 08:15 to 09:45
        - 10:00 to 11:30
        - 11:45 to 13:15
        - 13:30 to 15:00
        - 15:15 to 16:45
        - 17:00 to 18:30
        - 18:45 to 20:15
    - No **course** can be scheduled on saturday and thursday afternoon (from 13:30 to 20:15). No **course** ca be scheduled on Sunday.
    - Students must have at least one free slot a day. Either 11:45 to 13:15 or 13:30 to 15:00. This is to ensure they can eat.
    - **Courses** can be either **online** or **presential**. Respecting the previous condition regarding total amount of online hours.
    - Certain **courses** may require specific time slots due to logisitcal reasons. (e.g. lab courses requiring 3h sessions, thus, two back-to-back **timeslots**)
      
- To take place, each **course** needs:
    - An available room. (= A room where there is no course taking place)
    - A corresponding **class**
    - A **teacher** that can teach the **course**'s subject.
        - The **teacher** must be available. He can't give two courses at the same time.
        - The **teacher** may have preferred teaching time or days. The **schedule** should try to accomodate these perferences as much as possible.

- Room and Resource Allocation:
    - Scheduling must allocate regular or special rooms (e.g., labs or amphitheaters) based on course requirements.
    - Ensure adequate use of room resources while preventing overbooking or misuse of special-purpose spaces.


