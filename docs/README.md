# :calendar: Goodwing Timetabler :calendar: | v 0.1.3

## The Timetabling Problem, briefly

The disruptions caused by the COVID-19 pandemic have introduced new constraints in managing several complex problems of daily life. Among these, work schedule planning, an NP-hard optimization problem, has been particularly affected. This type of problem appears in various sectors such as administration, transportation, production, healthcare, and education.

In this context, we focus on the problem of optimizing university timetables. Before the pandemic, creating a timetable involved respecting certain constraints, such as the availability of teachers, classrooms, and permissible time slots. Any solution meeting these constraints was considered optimal. However, new constraints have emerged with the pandemic, such as limiting the number of students physically present, distance learning, hybrid formats, making the planning process more complex.

The objective of this project is to propose solutions, either exact or approximate, for the problem of course scheduling by considering both classical constraints (availability of teachers and classrooms) and new constraints related to teaching methods (in-person, distance, or hybrid), as well as balancing the workload for students according to these modalities.
The student will begin by conducting a literature review on the problem and then develop a new solution approach. Finally, tests will be conducted on a dataset to evaluate the solution and test its robustness.

## Setting up your instance

To easily setup your instance of the problem, go to `GoodwingTimetabler/UniversityInstance/UniversityGeneator.xlsx` and modify the excel sheets according to your problem.

## Running the app

The app runs with Python. Go inside the repo's folder in your terminal and, ensuring that python is installed, run:

`python .\GoodwingTimetabler`

Wait for the problem to generate, set a max time limit for the solver to do its job and once the problem is solved, you'll find your solution inside the `Outputs\excel\schedule.xlsx` file, alongisde the Schedule Intelligence report in the console (overlaps).

Sidenote: The CSP is poorly optimized at the moment (this is being taken care of !). Don't try to generate HUGE instances if your computer doesn't have a good enough CPU and RAM.

## Documentation

| File           | Description                      |
|------------------|----------------------------------|
| [Problem Definition](Problem_Definition.md) | Our problem, thoroughly defined |
| [Maths Constraints](Constraints_Maths.md) | The constraints of our problem, defined as mathematical relations |
| [Changelog](Changelog.md) | Changelog of the project |
| [How to Contribute](how_to_contribute.pdf) | How to help the project. (Needs an update !) |
