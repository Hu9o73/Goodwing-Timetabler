from myTests import test_csp_solver_performance
from csp import *
from util import ExcelScheduleManager

def run_app():
    generateScheduleUsingCSP()


def run_test():
    test_csp_solver_performance()


def generateScheduleUsingCSP():
    print("app running...\n")

    # Create the university
    my_univ = generateUniv2()
    print("Univ generated successfully : ", my_univ)
    print("Generating the CSP...")
    # Instantiate and solve the CSP
    scheduler = CSP(my_univ)

    # Output the generated schedules
    outputSchedulesFromCSP(scheduler)


def outputSchedulesFromCSP(csp_solver: CSP):
    # Excel output
    excel_manager = ExcelScheduleManager(csp_solver.university, csp_solver.generated_courses)
    excel_manager.generate_excel_schedule('./Outputs/excel/schedule.xlsx')