![Logo](./Images/Logos/Logo_v1_blanc.png)

# Goodwing Timetabler | v 0.3.1

## The Timetabling Problem: An Overview

Timetabling is a complex **constraint satisfaction problem (CSP)** that involves scheduling events while satisfying multiple constraints. This NP-hard optimization problem is prevalent in various sectors including **education, healthcare, transportation, and workforce management**.

In academic settings, the challenge lies in assigning courses to specific:
- Time slots
- Rooms
- Instructors

...while ensuring that constraints like availability, capacity, and fairness are met.

A valid timetable must respect multiple factors:
- **Resource constraints**: Availability of instructors, classrooms, and equipment
- **Time constraints**: No scheduling conflicts among courses and instructors
- **Student needs**: Avoiding overlapping courses and balancing workloads
- **Institutional policies**: Adhering to predefined academic structures, breaks, and weekend restrictions

Modern challenges such as **hybrid learning models** have introduced additional complexity to this already intricate problem.

## What Goodwing Timetabler Does

Goodwing Timetabler generates optimal or near-optimal course schedules for educational institutions. Starting from your university's specific parameters, the algorithm produces comprehensive timetables ensuring:

- All groups can attend sufficient courses to complete their subjects
- Teachers are assigned consistently (same teacher for all sessions of a subject for a group)
- Resources are allocated efficiently
- Institutional constraints are respected

## Setting Up Your Instance

### Step 1: Prepare Your Data
To set up your instance of the problem, navigate to `Inputs/University.xlsx` and modify the Excel sheets:

1. **University**: Basic settings like institution name, semester start date, duration
2. **Timeslots**: Define available time periods for courses
3. **Rooms**: Specify classrooms and their types
4. **Promotions**: Define study levels/years and their groups
5. **Subjects**: List all courses with hours required and color codes
6. **Teachers**: Enter faculty information and which subjects they can teach
7. **TeacherAvailability**: Optional sheet to specify when teachers are available

### Step 2: Important Considerations
- Ensure that the number of hours required to complete a subject is a multiple of a timeslot duration
- The starting day should be a Monday
- For best results, make sure you have enough teachers, rooms, and timeslots to satisfy all requirements

## Running the Application

### Option 1: Using the Installer

1. Download the latest installer from the releases page
2. Follow the installation steps
3. Double-click `GoodwingTimetabler.exe` to launch the application
4. Choose option 1 to start the AI solver
5. Enter a maximum time limit for the solver (in seconds)
6. Wait for the solution to be generated
7. Access your results in the `Outputs/excel/schedule.xlsx` file

### Option 2: Running with Python

If you prefer to run from source or want to modify the code:

1. Ensure Python is installed on your system
2. Clone or download the repository
3. Open a terminal in the repository folder
4. Run: `python .\GoodwingTimetabler`
5. Choose option 1 to start the AI solver
6. Enter a maximum time limit
7. Review the Schedule Intelligence report in the console when finished
8. Check `Outputs/excel/schedule.xlsx` for the complete timetable

### Option 3: Generating Input Templates

If you need to create a new instance from scratch:

1. Launch the application
2. Choose option 2 to generate input files
3. Edit the generated Excel files in the `Inputs` folder
4. Run the solver as described above

## Understanding the Results

### Excel Output Files

After running the solver, two key files are generated:

1. **schedule.xlsx**: Contains separate sheets for:
   - Each group's schedule
   - Each teacher's schedule 
   - Each room's allocation
   - Statistics sheet with usage metrics

2. **visual_timetable.xlsx**: A more user-friendly visual representation with:
   - Color-coded weekly schedules
   - Interactive navigation between sheets
   - Clear display of time slots and days

### Schedule Intelligence Report

The console displays a Schedule Intelligence report highlighting:

1. **Conflict Analysis**:
   - Room overlaps (soft constraint)
   - Teacher overlaps (soft constraint)

2. **Resource Utilization**:
   - Most used rooms
   - Teachers with heaviest workloads 
   - Busiest time slots

3. **Distribution Analysis**:
   - How courses are spread across the schedule
   - Balance of subjects across weeks

## Key Features

| Feature                                   | Implemented | Note                    |
|-------------------------------------------|-------------|-------------------------|
| **Constraints**                           |             | |
| Personalized University                   | Yes         | |
| Promotions and groups handling            | Yes         | |
| Personalized Timeslots and Timespan       | Yes         | |
| Unique schedule per week                  | Yes         | |
| Overlaps handling                         | Yes         | Soft constraint* |
| Lunch breaks                              | Yes         | |
| Slot restriction (weekends)               | Yes         | |
| Course balancing                          | Yes         | |
| Teacher availability                      | Yes         | |
| Online/Presential courses                 | Yes         | |
| Consistent teacher per subject-group      | Yes         | NEW! |
|                                           |             | |
| **Solving Methods**                       |             | |
| CSP Solver                                | Yes         | Using OR-Tools  |
| Genetic Algorithm, Neural Network         | No          | Not planned yet |

**Soft Constraint: The overlaps for teachers and rooms are treated as soft constraints to always yield a solution. It's then up to the user to identify where the overlaps occur by examining the Schedule Intelligence report in the terminal, and make manual adjustments if necessary.

## Performance Considerations

- For large instances, ensure your computer has sufficient CPU and RAM
- The solver's performance depends on the complexity of your constraints
- You can adjust the maximum solving time based on your needs
- Use the benchmark test (`pytest -s`) to evaluate performance on your system

## Additional Documentation

| File           | Description                      |
|------------------|----------------------------------|
| [Problem Definition](Problem_Definition.md) | Detailed problem specification |
| [Mathematical Constraints](Constraints_Maths.md) | Formal definition of constraints |
| [Changelog](Changelog.md) | Version history |

## Troubleshooting

If no solution is found:
1. Increase the maximum solving time
2. Add more resources (teachers, rooms, timeslots)
3. Verify that your teacher availability does not make a solution impossible