from myTests import test_csp_solver_performance
from csp import *
from util import ExcelScheduleManager, init_template, create_availability_template
import os
import subprocess


def run_app():
    print("app running...\n\n\n")
    print("=========== Goodwing Timetabler v0.4.0 ===========\n\n")

    print("Choose an option:")
    print("[1] Start the AI solver")
    print("[2] Generte Input files")
    user_input = input("")

    try:
        user_input = int(user_input)
    except:
        print("Please enter a valid input ...")
        return
    
    if user_input == 1:
        print("\nStarting solver ...")
        generateScheduleUsingCSP()
    elif user_input == 2:
        print("\nGenerating files...")
        init_template("./Inputs/")
        print("Done !")
    else:
        print("Please enter a valid number ...")

    # To let console stay open upon app end of execution (important if we run the .exe !)
    input("\nPress Enter to exit...")


def run_test():
    test_csp_solver_performance()


def generateScheduleUsingCSP():

    # Create the university
    my_univ = generateUniv2("./Inputs/")
    print("Univ generated successfully : ", my_univ)
    print("Generating the CSP...")
    # Instantiate and solve the CSP
    scheduler = CSP(my_univ)

    # Output the generated schedules
    outputSchedulesFromCSP(scheduler)
    
    # Run the Plugin to send emails to teachers
    print("\n\nSending emails to teachers...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")) # Find the root directory of the project dynamically
    file_path_emails = os.path.join(project_root, "Plugins", "Send-Mail-To-Teachers") # Construct the correct absolute path
    file_path_emails = file_path_emails.replace("\\", "/") # Ensure forward slashes for Windows compatibility
    subprocess.run(["python", "send_emails.py"], cwd=file_path_emails) # Run send_emails.py from the correct directory

    # Run the Frontend to visualize the intelligence report
    print("\n\nDisplaying the intelligence report...")
    file_path_frontend_ir = os.path.join(project_root, "Frontend", "Intelligence-Report") # Construct the correct absolute path
    file_path_frontend_ir = file_path_frontend_ir.replace("\\", "/") # Ensure forward slashes for Windows compatibility
    subprocess.run(["streamlit", "run", "display_intelligence_report.py"], cwd=file_path_frontend_ir) # Run display_intelligence_report.py from the correct directory



def outputSchedulesFromCSP(csp_solver: CSP):
    # Excel output
    excel_manager = ExcelScheduleManager(csp_solver.university, csp_solver.generated_courses)
    excel_manager.generate_excel_schedule('./Outputs/excel/schedule.xlsx')
    excel_manager.create_visual_timetable('./Outputs/excel/visual_timetable.xlsx')