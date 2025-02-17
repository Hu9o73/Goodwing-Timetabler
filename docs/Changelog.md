# Changelog

## v0.1.3

- Added the opportunity to stop the solving process when the first feasible solution is found.
    - This means:
        - No room conflict
        - No teacher conflict
    - Giving more time to the CSP will make it minimize the schedule balance. For instance:
        - First feasible solution might set all courses to take place on the first two weeks
        - An optimized (and thus more balanbced) solution will have its courses spread across the available timeslots.
- Fixed the solver overshooting its solving-time limit.

## v0.1.2

- The terminal output specifies if the solution is optimal or not.
- Optimized the `noRoomOverlap()` function.
- v0.1.1 and prior versions created O(n²) boolean variables (where n is the number of courses)
- The optimized version creates only O(n × r) variables where r is the number of rooms
    - For a schedule with 100 courses and 10 rooms, this reduces from ~10,000 variables to ~1,000 variables
- Time reducton on the same instance of the problem\* (To obtain a feasible solution) for v0.1.1 and v0.1.2 :
    - Instantiation time further reduced by 50%.
        - \- 97% since v0.1.0
    - Computation time futher reduced by 67% on average.
        - \- 83% since v0.1.0

## v0.1.1

- Heavily optimized the `teacherAvailabilityConstraint()` function. Reduced the problem's instantiation time.
    - Uses direct domain restrictions instead of multiple boolean variables
    - Handles the constraints at the teacher selection level rather than the timeslot level
    - Reduces the number of constraints from O(n * m * t) to O(n * t) where:
        - n = number of courses
        - m = number of timeslots
        - t = number of teachers
- Time reducton on the same instance of the problem\* (To obtain a feasible solution) for v0.1.0 and v0.1.1 :
    - Instantiation time reduced by 95%.
    - Computation time reduced by 47% on average.

- \* *Excel generation file available in commit `c684ef4` (corresponding to v0.1.1). Averages of tests on 5 runs. Feasible solution is guaranteed.* 

## v0.1.0

- First fully usable user-friendly version !
- Added the ExcelScheduleManager to create the new output file.
- Changed the output to be an Excel file (easier to read !) containing:
    - Group schedules
    - Teacher schedules
    - Room schedules
- Fixed the Teacher Availability function to work for schedules of more than 7 days.

## v0.0.6

- Added problem instance generation using an excel file.
    - Makes things way easier to test different instances !
- Added live timer while solving the CSP to let the user know the program isn't dead (as it may run for long...)
- Fixed `noRoomOverlap()` and `noTeacherOverlap()`

## v0.0.5

- Added the ScheduleIntelligence class to build conflict reports and gather intel about our schedule.
- Added conflicts penalties to handle room and teacher overlaps as soft constraints.
- Modified `noRoomOverlap()` and `noTeacherOverlap()` to handle these constraints as soft.
    - Now, if we don't have enough rooms or teachers, we still output a schedule and its conflicts, so someone can hypothetically solve manually !
- Removed many output debug prints. Added an intelligence report to the console output, with the eventual conflicts.

## v0.0.4

- Added teachers availability.
- Fixed schedule visualization showing too many courses.

## v0.0.3

- Added course balancing:
    - First gist of course balancing, trying to spread them accross the week.

- Restricted timeslots:
    - Saturday afternoon's and Sunday's timeslots are now restricted, no course can take place on these timeslots.

## v0.0.2

- Added teacher support:
    - Each course now has a corresponding teacher assigned.
    - The teacher must be able to teach the subject.
    - The teacher's preferred timeslots aren't supported yet. A teacher is considered being able to work all day on all timeslots (for now).

- Added lunch break enforcement:
    - Made sure that no course can be scheduled on the 3rd timeslot of each day (between 11:30 and 13:15) so students and teachers can eat.

- Fixed coloring on the pdf output.

## v0.0.1

- Implemented OR-Tools' CSP to start solving the problem
- Basic course assignement:
    - Assign an x amount of courses per group per subject depending on the hours required to complete the subject.
    - Ensure that all course is assigned to a timeslot.
    - Ensuring that a group can't have 2 courses assigned to the same timeslot.

- Ensuring no room overlap:
    - Made sure that 2 courses can't be assigned to the same room if they're on the same timeslot.