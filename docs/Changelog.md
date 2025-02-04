# Changelog

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