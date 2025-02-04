from csp import *
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import datetime as dt

def append_courses_to_yaml_file(courses: List[Course], file_path, groupName: str = 'NoName'):
    """
    Appends the YAML representation of a list of Course objects to a .yml file.\n
    Parameters:\n
    - courses: List[Course] | A list of Course objects.
    - file_path: str | The path to the .yml file.
    - groupName: str | The group's name
    """
    yaml_entries = []
    
    for course in courses:
        entry = course.to_yaml_entry()
        yaml_entries.append(entry)

    yaml_content = yaml.dump(yaml_entries, default_flow_style=False)

    with open(file_path, 'w') as file:
        file.write(yaml_content)

    plot_schedule(yaml_content, f'./Outputs/png/{groupName}.png')


def plot_schedule(yaml_data, save_path=None):
    # Load YAML
    schedule = yaml.safe_load(yaml_data)
    
    # Days of the week order
    days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    day_to_num = {day: i for i, day in enumerate(days_order)}
    
    # Convert time to numerical format for plotting
    def time_to_float(time_str):
        time_obj = dt.datetime.strptime(time_str, "%H:%M").time()
        return time_obj.hour + time_obj.minute / 60
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_yticks(range(len(days_order)))
    ax.set_yticklabels(days_order)
    ax.set_xticks(range(8, 22, 1))  # Time from 8:00 to 22:00
    ax.set_xticklabels([f"{h}:00" for h in range(8, 22)])
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Plot each schedule entry
    patches = []
    for entry in schedule:
        day = entry['days']
        start, end = entry['time'].split(' - ')
        start_time, end_time = time_to_float(start), time_to_float(end)
        duration = end_time - start_time
        
        # Assign color
        color = "#" + entry['color']
        
        # Add rectangle to the plot
        rect = mpatches.Rectangle((start_time, day_to_num[day]), duration, 0.8, color=color, alpha=0.8)
        ax.add_patch(rect)
        
        # Text inside the block
        ax.text(start_time + 0.1, day_to_num[day] + 0.4, entry['name'], fontsize=6, color='white', va='center', ha='left', weight='bold')
    
    # Formatting
    ax.set_ylim(-0.5, len(days_order) - 0.5)
    ax.set_xlim(8, 22)
    ax.set_xlabel("Time")
    ax.set_ylabel("Day of the Week")
    ax.set_title("Weekly Schedule")

    # Save or show plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
