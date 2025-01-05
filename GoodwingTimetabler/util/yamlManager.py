from csp import *
import yaml

def append_courses_to_yaml_file(courses: List[Course], file_path):
    """
    Appends the YAML representation of a list of Course objects to a .yml file.\n
    Parameters:\n
    - courses: List[Course] | A list of Course objects.
    - file_path: str | The path to the .yml file.
    """
    # Prepare a list of YAML-compatible dictionaries for all courses
    yaml_entries = []
    for course in courses:
        yaml_entries.append(course.to_yaml_entry())

    # Convert to YAML format
    yaml_content = yaml.dump(yaml_entries, default_flow_style=False)

    # Append to the file
    with open(file_path, 'w') as file:
        file.write(yaml_content)