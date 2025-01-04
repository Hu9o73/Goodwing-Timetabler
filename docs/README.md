# :calendar: Goodwing Timetabler :calendar:

## The Timetabling Problem, briefly

The disruptions caused by the COVID-19 pandemic have introduced new constraints in managing several complex problems of daily life. Among these, work schedule planning, an NP-hard optimization problem, has been particularly affected. This type of problem appears in various sectors such as administration, transportation, production, healthcare, and education.

In this context, we focus on the problem of optimizing university timetables. Before the pandemic, creating a timetable involved respecting certain constraints, such as the availability of teachers, classrooms, and permissible time slots. Any solution meeting these constraints was considered optimal. However, new constraints have emerged with the pandemic, such as limiting the number of students physically present, distance learning, hybrid formats, making the planning process more complex.

The objective of this project is to propose solutions, either exact or approximate, for the problem of course scheduling by considering both classical constraints (availability of teachers and classrooms) and new constraints related to teaching methods (in-person, distance, or hybrid), as well as balancing the workload for students according to these modalities.
The student will begin by conducting a literature review on the problem and then develop a new solution approach. Finally, tests will be conducted on a dataset to evaluate the solution and test its robustness.

## Running the app

The app runs with Python. Download the repo, go to the file location in your terminal and, ensuring that python is installed, run:

`python .\GoodwingTimetabler`

You'll run whatever function is called in `GoodwingTimetabler/__main__.py`.
You may want to check if `run_app` or `run_test` is called before running the project. (This will be cleaned and polish later on in the development, there's no much user-friendliness so far...)

## Documentation

| File           | Description                      |
|------------------|----------------------------------|
| [Problem Definition](Problem_Definition.md) | Our problem, thoroughly defined |
| [Maths Constraints](Constraints_Maths.md) | The constraints of our problem, defined as mathematical relations |
| [Acknowledgements](ACKNOWLEDGEMENTS.md) | Acknowledgements, references to helpful projects |