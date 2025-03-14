# Changelog

## v0.4.0

- Added a soft constraint to minimize students having to go back to school after an online class.
- Added a soft constraint to minimize late courses.
    - A 'late course' is a course taking place on one of the last 2 timeslots of each day.

## v0.3.1

- Added a soft constraint to minimize the number of gaps between courses on the same day.
- Added a number of found solutions tracker.
- Added a penalties (objective value) tracker.
    - Note: We're trying to minimize this, and remember that optimal is not necessarily perfect ! (You don't HAVE to reach 0 to have an optimal solution).

## v0.3.0

- Added consistency regarding teacher assignement
    - Teachers are now assigned to groups rather than individual courses !
- Rewrote readme file to ease app usage !

## v0.2.5

- Included teacher availability in the excel instantiator file !
- Fixed `teacherAvailabilityConstraint` function.
- Added functions to let user create a basic university template they can customize.

## v0.2.4

- Added a more visually pleasing output !
    - Navigate and see groups, rooms and teachers schedules for each week, on an 'actual' timetable.

## v0.2.3

- Added a soft constraint to unstack subjects.
    - This is to avoid finishing a subject the first week and then have 5 weeks without it, easing the workload !

## v0.2.2

- Added the online/presential course support
    - To include online courses to your scheduler, add a room called "online".
    - For each group, no more than 30% of the courses per subject can take place online.
- Modified `noRoomOverlap()` not to apply to room 'online'.
- Changed the numbers of cores used to 4, to reduce impact on RAM !

## v0.2.1

- Added an installer, installing the app alongside a .exe file that anyone can run !
    - Users don't need to install python or any libraries anymore, it can all be done via the installer !
    - Note: As the installer is a compiled file, modifications you make to the code on your forks won't affect the installer.
    - Users install the .exe, `Inputs` and `Outputs` folders. Makes the app easier to use for non-programmers.
- Took the default input folder out of the `/GoodwingTimetabler` folder.
    - Past input folder wasn't completely deleted and is still the default folder if no argument is passed in `GenerateUniv2()` in `app/main.py`

## v0.2.0

- Optimization at its finest !
- This version optimized the CSP (see detail in versions v0.1.1 to v0.1.7).
- Added unitary tests, to compare the computational time.
- Added tracking of RAM and CPU.
- Few bug fix.

## v0.1.7

- Fixed `restrictWeekendTimeslot()`, now working for days with any number of timeslot per day (previously 7).
- Fixed instantiation, consider the possibility that the user doesn't provide an integer for the number of max seconds, the program responds accordingly. 

## v0.1.6

- Optimized `ensureLunchBreak()`, reducing the number of constraints generated by this function by 98%.
    - Reduced complexity from $o(N \times L)$ to $o(N)$.
        - N being the number of courses
        - L being the number of lunch break slots 
- Time reducton on the same instance of the problem\* (To obtain a feasible solution) from v0.1.5 to v0.1.6 :
    - Instantiation time reduced by 18%.
    - Computation time reduced by 10% on average.
- Modified benchmark to run only upon push on the main branch.

## v0.1.5

- Added benchmark tests. (Call `pytest -s` to run the tests.)
- Cleaned `app` and `myTests` modules.
- Added a git actions to ensure the algorithm runs smoothly !

## v0.1.4

- Added a Logo to the project.
- Added a RAM and CPU usage tracker.
- Reverted changes done to `noRoomOverlap()` in `v0.1.2` as it turned the constraint to hard, we want it soft !
    - Took the function from `v0.1.1`

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
- Optimized the `noRoomOverlap()` function. *(Bugged ! Fixed in `v0.1.4`)*

## v0.1.1

- Heavily optimized the `teacherAvailabilityConstraint()` function. Reduced the problem's instantiation time.
    - Uses direct domain restrictions instead of multiple boolean variables
    - Handles the constraints at the teacher selection level rather than the timeslot level
    - Reduces the number of constraints from O(n * m * t) to O(n * t) where:
        - n = number of courses
        - m = number of timeslots
        - t = number of teachers
- Time reducton on the same instance of the problem\* (To obtain a feasible solution) from v0.1.0 to v0.1.1 :
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
