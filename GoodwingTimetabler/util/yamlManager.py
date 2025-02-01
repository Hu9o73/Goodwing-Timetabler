from csp import *
import yaml

def append_courses_to_yaml_file(courses: List[Course], file_path):
    """
    Appends the YAML representation of a list of Course objects to a .yml file.\n
    Parameters:\n
    - courses: List[Course] | A list of Course objects.
    - file_path: str | The path to the .yml file.
    """
    yaml_entries = []
    
    print("\nDEBUG: Converting to YAML entries:")
    for course in courses:
        entry = course.to_yaml_entry()
        print(f"Subject: {course.subject.name}")
        print(f"YAML entry: {entry}")
        yaml_entries.append(entry)

    yaml_content = yaml.dump(yaml_entries, default_flow_style=False)
    
    print("\nDEBUG: Final YAML content:")
    print(yaml_content)

    with open(file_path, 'w') as file:
        file.write(yaml_content)