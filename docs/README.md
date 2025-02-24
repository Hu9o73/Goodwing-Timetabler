![Logo](./Images/Logos/Logo_v1_blanc.png)
 
# Goodwing Timetabler | v 0.2.2

## The Timetabling Problem, briefly

Timetabling is a well-known **constraint satisfaction problem (CSP)** that involves scheduling a set of events while satisfying a range of constraints. This problem is prevalent in various fields, including **education, healthcare, transportation, and workforce management**. In the context of universities, the challenge lies in assigning courses to specific time slots, rooms, and instructors while ensuring that constraints such as availability, capacity, and fairness are met.  

Timetabling is considered an **NP-hard optimization problem**, meaning that finding an optimal solution becomes computationally complex as the number of variables and constraints increases. A valid timetable must respect multiple factors, including:  

- **Resource constraints**: Availability of instructors, classrooms, and equipment.  
- **Time constraints**: Ensuring no scheduling conflicts among courses and instructors.  
- **Student needs**: Avoiding overlapping courses and balancing workloads.  
- **Institutional policies**: Adhering to predefined academic structures, breaks, and weekend restrictions.  

Modern challenges, such as **hybrid learning models** , have introduced additional constraints, making the problem even more intricate. To tackle this, solutions range from **exact methods** (such as integer programming and constraint solvers) to **heuristic and metaheuristic approaches** (such as genetic algorithms and simulated annealing). Our goal is to generate **efficient, practical, and adaptable** timetables that meet institutional and individual requirements.

## What does the Goodwing Timetabler do ?

From a University instance that you can set up, running the algorithm will yield an optimal or sub-optimal solution regarding the schedule of all the groups. Ensuring all groups can attend sufficient courses to complete all their subjects.

## Setting up your instance

To easily setup your instance of the problem, go to `Inputs/University.xlsx` and modify the excel sheets according to your problem.

*Notes:* 
- *Ensure that the number of hours required to complete a subject is a multiple of a timeslot duration ! Otherwise you might see that a course is missing or extra.*
- *Ensure that the starting day is a monday !*

## Running the app

### With the installer

Go the the releases page and download the latest version of the installer. Follow the installation steps and double-click `GoodwingTimetabler.exe` !

You can easily access Inputs and Outputs folders to modify your instance of the problem and access your result ! 

### With python

If you feel like programming and modifying the source code, you can run the app with Python. Go inside the repo's folder in your terminal and, ensuring that python is installed, run:

`python .\GoodwingTimetabler`

Wait for the problem to generate, set a max time limit for the solver to do its job and once the problem is solved, you'll find your solution inside the `Outputs\excel\schedule.xlsx` file, alongisde the Schedule Intelligence report in the console (overlaps).

You can also run `pytest -s` to test the algorithm's performances (takes time).

Sidenote: Don't try to generate HUGE instances if your computer doesn't have a good enough CPU and RAM.

## Roadmap
| Feature                                   | Implemented | Note                    |
|-------------------------------------------|-------------|-------------------------|
| **Constraints**                           |             | |
| Personnalized University                  | Yes         | |
| Promotions and groups handling            | Yes         | |
| Personnalized Timeslots and Timespan      | Yes         | |
| Unique schedule per week                  | Yes         | |
| Overlaps handling                         | Yes         | Soft constraint* |
| Lunch breaks                              | Yes         | |
| Slot restriction (weekends)               | Yes         | |
| Course balancing                          | Yes         | |
| Teacher availability                      | Partially   | No easy access from the excel yet |
| Online/Presential courses                 | Yes         | |
| Special room handling                     | No          | |
|                                           |             | |
| **Means of solving the problem**          |             | |
| CSP Solver                                | Yes         | Using OR-Tools  |
| Genetic Algorithm, Neural Network         | No          | Not planned yet, but the idea sounds good !|

**Soft Constraint: The overlaps for teachers and rooms are treated as soft constraints to always yield a solution. It's then up to the user to find a feasible solution by examining where are the overlaps. This is done looking at the Schedule Inetlligence in the terminal, after the algorithm ran.*

## Documentation

| File           | Description                      |
|------------------|----------------------------------|
| [Problem Definition](Problem_Definition.md) | Our problem, thoroughly defined |
| [Maths Constraints](Constraints_Maths.md) | The constraints of our problem, defined as mathematical relations |
| [Changelog](Changelog.md) | Changelog of the project |
