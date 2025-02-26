import pandas as pd

# ExcelScheduleManager
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder
from openpyxl.worksheet.filters import FilterColumn, Filters
import datetime as dt
from typing import List, Dict
from collections import defaultdict
from csp import University

def createCSV(gen_dir: str = './GoodwingTimetabler/UniversityInstance/'):
    sheets = ['University', 'Timeslots', 'Promotions', 'Subjects', 'Teachers', 'Rooms']
    dfs = []
    for idx, sheet_name in enumerate(sheets):
        dfs.append(pd.read_excel(gen_dir+'University.xlsx', sheet_name))
        dfs[idx].to_csv(f'{gen_dir}csv/{sheet_name}.csv', index=False)

    # Print the CSV
    #for df in dfs:
    #    pd.set_option('display.max_columns', 1000)
    #    pd.set_option('display.width', 1000)
    #    print(df)
    #    print('\n')

class ExcelScheduleManager:
    def __init__(self, university: University, generated_courses):
        self.university = university
        self.courses = generated_courses
        self.wb = Workbook()
        self.time_slots = university.time_ranges
        
    def format_time(self, time_obj):
        return time_obj.strftime("%H:%M")

    def get_week_number(self, date):
        return (date - self.university.timeslots[0].day).days // 7 + 1

    def setup_sheet_structure(self, ws):
        # Headers
        headers = ['Week', 'Day', 'Time Slot', 'Subject', 'Teacher', 'Room']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')

        # Add filters
        ws.auto_filter.ref = f'A1:F1'
        
        # Set column widths
        dim_holder = DimensionHolder(worksheet=ws)
        
        widths = [10, 15, 20, 30, 25, 15]  # Adjusted widths for each column
        for col, width in enumerate(widths, 1):
            dim_holder[get_column_letter(col)] = ColumnDimension(ws, min=col, max=col, width=width)
        
        ws.column_dimensions = dim_holder

    def add_course_to_sheet(self, ws, row, course, week_num):
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_of_week = day_names[course.timeslot.day.weekday()]
        
        # Data to insert
        data = [
            week_num,
            day_of_week,
            f"{self.format_time(course.timeslot.start)} - {self.format_time(course.timeslot.end)}",
            course.subject.name,
            f"{course.teacher.first_name} {course.teacher.last_name}",
            course.room.name
        ]
        
        # Insert data
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = value
            cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Add color to subject cell
            if col == 4:  # Subject column
                cell.fill = PatternFill(start_color=course.subject.color, 
                                      end_color=course.subject.color, 
                                      fill_type="solid")
                # Adjust font color for better readability
                brightness = sum(int(course.subject.color[i:i+2], 16) for i in (0, 2, 4)) / 3
                cell.font = Font(color="FFFFFF" if brightness < 128 else "000000")

        # Add border
        border = Border(left=Side(style='thin'), 
                       right=Side(style='thin'),
                       top=Side(style='thin'),
                       bottom=Side(style='thin'))
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = border

    def create_group_schedule(self, group_name, group_courses):
        ws = self.wb.create_sheet(title=f"Group_{group_name}")
        self.setup_sheet_structure(ws)
        
        row = 2
        for course in sorted(group_courses, 
                           key=lambda x: (self.get_week_number(x.timeslot.day), 
                                        x.timeslot.day, 
                                        x.timeslot.start)):
            week_num = self.get_week_number(course.timeslot.day)
            self.add_course_to_sheet(ws, row, course, week_num)
            row += 1

    def create_teacher_schedule(self, teacher, teacher_courses):
        ws = self.wb.create_sheet(title=f"Teacher_{teacher.last_name}")
        self.setup_sheet_structure(ws)
        
        row = 2
        for course in sorted(teacher_courses, 
                           key=lambda x: (self.get_week_number(x.timeslot.day), 
                                        x.timeslot.day, 
                                        x.timeslot.start)):
            week_num = self.get_week_number(course.timeslot.day)
            self.add_course_to_sheet(ws, row, course, week_num)
            row += 1

    def create_room_schedule(self, room, room_courses):
        ws = self.wb.create_sheet(title=f"Room_{room.name}")
        self.setup_sheet_structure(ws)
        
        row = 2
        for course in sorted(room_courses, 
                           key=lambda x: (self.get_week_number(x.timeslot.day), 
                                        x.timeslot.day, 
                                        x.timeslot.start)):
            week_num = self.get_week_number(course.timeslot.day)
            self.add_course_to_sheet(ws, row, course, week_num)
            row += 1

    def create_statistics_sheet(self):
        ws = self.wb.create_sheet(title="Statistics")
        
        # Style for headers
        header_style = Font(bold=True)
        header_fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
        
        # Group Statistics
        ws['A1'] = "Group Statistics"
        ws['A1'].font = header_style
        
        headers = ['Group', 'Total Hours', 'Subjects', 'Teachers']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col)
            cell.value = header
            cell.font = header_style
            cell.fill = header_fill
        
        row = 3
        group_stats = defaultdict(lambda: {'hours': 0, 'subjects': set(), 'teachers': set()})
        
        for course in self.courses:
            stats = group_stats[course.group.name]
            duration = (course.timeslot.end.hour - course.timeslot.start.hour + 
                       (course.timeslot.end.minute - course.timeslot.start.minute) / 60)
            stats['hours'] += duration
            stats['subjects'].add(course.subject.name)
            stats['teachers'].add(f"{course.teacher.first_name} {course.teacher.last_name}")
        
        for group, stats in group_stats.items():
            ws.cell(row=row, column=1, value=group)
            ws.cell(row=row, column=2, value=f"{stats['hours']:.1f}")
            ws.cell(row=row, column=3, value=len(stats['subjects']))
            ws.cell(row=row, column=4, value=len(stats['teachers']))
            row += 1
        
        # Teacher Statistics
        row += 2
        ws.cell(row=row, column=1, value="Teacher Statistics").font = header_style
        row += 1
        
        headers = ['Teacher', 'Total Hours', 'Groups', 'Subjects']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = header_style
            cell.fill = header_fill
        
        row += 1
        teacher_stats = defaultdict(lambda: {'hours': 0, 'groups': set(), 'subjects': set()})
        
        for course in self.courses:
            teacher = f"{course.teacher.first_name} {course.teacher.last_name}"
            stats = teacher_stats[teacher]
            duration = (course.timeslot.end.hour - course.timeslot.start.hour + 
                       (course.timeslot.end.minute - course.timeslot.start.minute) / 60)
            stats['hours'] += duration
            stats['groups'].add(course.group.name)
            stats['subjects'].add(course.subject.name)
        
        for teacher, stats in teacher_stats.items():
            ws.cell(row=row, column=1, value=teacher)
            ws.cell(row=row, column=2, value=f"{stats['hours']:.1f}")
            ws.cell(row=row, column=3, value=len(stats['groups']))
            ws.cell(row=row, column=4, value=len(stats['subjects']))
            row += 1
        
        # Adjust column widths
        for col in range(1, 5):
            ws.column_dimensions[get_column_letter(col)].width = 20

    def generate_excel_schedule(self, output_path):
        # Remove default sheet
        self.wb.remove(self.wb.active)
        
        # Group schedules
        group_courses = defaultdict(list)
        for course in self.courses:
            group_courses[course.group.name].append(course)
        
        for group_name, courses in group_courses.items():
            self.create_group_schedule(group_name, courses)
        
        # Teacher schedules
        teacher_courses = defaultdict(list)
        for course in self.courses:
            teacher_courses[course.teacher].append(course)
        
        for teacher, courses in teacher_courses.items():
            self.create_teacher_schedule(teacher, courses)
        
        # Room schedules
        room_courses = defaultdict(list)
        for course in self.courses:
            room_courses[course.room].append(course)
        
        for room, courses in room_courses.items():
            self.create_room_schedule(room, courses)
        
        # Statistics sheet
        self.create_statistics_sheet()
        
        # Save the workbook
        self.wb.save(output_path)
        print(f"Basic timetable saved to {output_path}")

    def create_visual_timetable(self, output_path="./Outputs/excel/visual_timetable.xlsx"):
        """
        Creates a visual Excel timetable with days as columns and timeslots as rows.
        Creates separate sheets for each week to handle unique weekly schedules.
        Each entity (group, teacher, room) gets its own set of weekly sheets.
        Includes an organized index page with separate columns for groups, teachers, and rooms.
        
        Parameters:
        - output_path: str | Path to save the Excel file
        """
        from openpyxl import Workbook
        from openpyxl.styles import PatternFill, Alignment, Font, Border, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.hyperlink import Hyperlink
        from openpyxl.drawing.image import Image
        import datetime as dt
        from collections import defaultdict

        wb = Workbook()
        wb.remove(wb.active)  # Remove the default sheet
        
        # Format time ranges for row headers
        time_range_labels = [f"{self.format_time(start)} - {self.format_time(end)}" 
                            for start, end in self.university.time_ranges]
        
        # Day names for column headers
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Create border styles
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        
        # Calculate the number of weeks in the schedule
        start_date = self.university.timeslots[0].day
        end_date = self.university.timeslots[-1].day
        days_diff = (end_date - start_date).days
        total_weeks = (days_diff // 7) + 1
        
        # Function to get week number for a date (relative to start_date)
        def get_week_number(date):
            days_from_start = (date - start_date).days
            return days_from_start // 7
        
        # Create the index sheet first
        index = wb.create_sheet(title="Index")
        
        # Keep track of all sheets for organized index
        sheet_info = {
            'Groups': [],
            'Teachers': [],
            'Rooms': []
        }
        
        # Function to add navigation button back to index
        def add_back_to_index_button(worksheet):
            # Add a text hyperlink in the top-right corner
            cell = worksheet.cell(row=1, column=8)  # Use H1 cell
            cell.value = "Back to Index"
            cell.hyperlink = "#Index!A1"
            cell.font = Font(color="0563C1", underline="single", bold=True)
            cell.alignment = Alignment(horizontal='right')
        
        # Function to create a visual timetable sheet for a specific week
        def setup_visual_sheet(entity_name, entity_type, week_num, courses_by_timeslot):
            sheet_type = f"{entity_type}s"  # Convert to plural for categorization
            
            # Format sheet name
            sheet_name = f"{entity_type}_{entity_name}_W{week_num+1}"
            # Truncate sheet name if too long (Excel limit is 31 chars)
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:28] + "..."
            
            # Store sheet info for index
            sheet_info[sheet_type].append({
                'name': entity_name,
                'week': week_num + 1,
                'sheet_name': sheet_name
            })
            
            ws = wb.create_sheet(title=sheet_name)
            
            # Set up column widths
            for col in range(1, 9):  # 1 for time column + 7 days + 1 for back button
                width = 20 if col == 1 else 25
                ws.column_dimensions[get_column_letter(col)].width = width
            
            # Set up row heights
            for row in range(1, len(time_range_labels) + 3):
                ws.row_dimensions[row].height = 60
            
            # Add header with week information
            week_start = start_date + dt.timedelta(days=week_num*7)
            week_end = min(week_start + dt.timedelta(days=6), end_date)
            week_header = f"Week {week_num+1}: {week_start.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
            
            # Add the entity name and week info in cell A1
            ws.merge_cells('A1:G1')
            header_cell = ws.cell(row=1, column=1)
            header_cell.value = f"{entity_type}: {entity_name} - {week_header}"
            header_cell.font = Font(bold=True, size=14)
            header_cell.alignment = Alignment(horizontal='center', vertical='center')
            header_cell.fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
            
            # Add back to index button
            add_back_to_index_button(ws)
            
            # Add day headers (row 2)
            ws.cell(row=2, column=1).value = "Time Slot"
            ws.cell(row=2, column=1).font = Font(bold=True)
            ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=2, column=1).border = thin_border
            ws.cell(row=2, column=1).fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
            
            for i, day in enumerate(day_names):
                cell = ws.cell(row=2, column=i+2)
                cell.value = day
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                cell.fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
            
            # Add time slots as row headers
            for i, time_label in enumerate(time_range_labels):
                cell = ws.cell(row=i+3, column=1)
                cell.value = time_label
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                cell.fill = PatternFill(start_color="F0F0F0", end_color="F0F0F0", fill_type="solid")
            
            # Create empty grid with borders
            for row in range(3, len(time_range_labels) + 3):
                for col in range(2, 9):
                    cell = ws.cell(row=row, column=col)
                    cell.border = thin_border
            
            # Fill in the courses for this week
            for (day_idx, time_idx), course_list in courses_by_timeslot.items():
                if 0 <= day_idx < 7 and 0 <= time_idx < len(time_range_labels):
                    row = time_idx + 3
                    col = day_idx + 2
                    
                    if course_list:  # If there are courses in this timeslot
                        # Format the text for multiple courses (if more than one)
                        if len(course_list) > 1:
                            text = "\n".join([f"{c.subject.name} ({c.room.name})" for c in course_list])
                            cell = ws.cell(row=row, column=col)
                            cell.value = text
                            cell.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
                            cell.font = Font(size=8)  # Smaller font for multiple entries
                        else:
                            # Single course, more detailed formatting
                            course = course_list[0]
                            cell = ws.cell(row=row, column=col)
                            cell.value = f"{course.subject.name}\n{course.teacher.first_name} {course.teacher.last_name}\n({course.room.name})"
                            cell.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
                            
                            # Color based on subject
                            color = course.subject.color
                            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
                            
                            # Set font color based on background brightness
                            brightness = sum(int(color[i:i+2], 16) for i in (0, 2, 4)) / 3
                            cell.font = Font(color="FFFFFF" if brightness < 128 else "000000")
        
        # Process group schedules - organize by group, week, day, and timeslot
        group_schedules = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for course in self.courses:
            date = course.timeslot.day
            week_num = get_week_number(date)
            day_idx = date.weekday()  # 0 for Monday, 6 for Sunday
            
            # Find the time range index
            time_idx = None
            for i, (start, end) in enumerate(self.university.time_ranges):
                if course.timeslot.start == start and course.timeslot.end == end:
                    time_idx = i
                    break
            
            if time_idx is not None:
                group_schedules[course.group.name][week_num][(day_idx, time_idx)].append(course)
        
        # Create visual timetable for each group and week
        for group_name, weeks in group_schedules.items():
            for week_num, courses_by_timeslot in weeks.items():
                setup_visual_sheet(group_name, "Group", week_num, courses_by_timeslot)
        
        # Process teacher schedules - organize by teacher, week, day, and timeslot
        teacher_schedules = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for course in self.courses:
            teacher_name = f"{course.teacher.last_name}_{course.teacher.first_name}"
            date = course.timeslot.day
            week_num = get_week_number(date)
            day_idx = date.weekday()
            
            time_idx = None
            for i, (start, end) in enumerate(self.university.time_ranges):
                if course.timeslot.start == start and course.timeslot.end == end:
                    time_idx = i
                    break
            
            if time_idx is not None:
                teacher_schedules[teacher_name][week_num][(day_idx, time_idx)].append(course)
        
        # Create visual timetable for each teacher and week
        for teacher_name, weeks in teacher_schedules.items():
            for week_num, courses_by_timeslot in weeks.items():
                setup_visual_sheet(teacher_name, "Teacher", week_num, courses_by_timeslot)
        
        # Process room schedules - organize by room, week, day, and timeslot
        room_schedules = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for course in self.courses:
            date = course.timeslot.day
            week_num = get_week_number(date)
            day_idx = date.weekday()
            
            time_idx = None
            for i, (start, end) in enumerate(self.university.time_ranges):
                if course.timeslot.start == start and course.timeslot.end == end:
                    time_idx = i
                    break
            
            if time_idx is not None:
                room_schedules[course.room.name][week_num][(day_idx, time_idx)].append(course)
        
        # Create visual timetable for each room and week
        for room_name, weeks in room_schedules.items():
            for week_num, courses_by_timeslot in weeks.items():
                setup_visual_sheet(room_name, "Room", week_num, courses_by_timeslot)
        
        # Now build the index page with three separate columns
        index = wb.worksheets[0]  # Get the index sheet we created earlier
        
        # Set up column widths
        index.column_dimensions['A'].width = 25
        index.column_dimensions['B'].width = 10
        index.column_dimensions['C'].width = 5  # Spacer
        index.column_dimensions['D'].width = 25
        index.column_dimensions['E'].width = 10
        index.column_dimensions['F'].width = 5  # Spacer
        index.column_dimensions['G'].width = 25
        index.column_dimensions['H'].width = 10
        
        # Add title
        index.merge_cells('A1:H1')
        title_cell = index.cell(row=1, column=1)
        title_cell.value = "VISUAL TIMETABLE INDEX"
        title_cell.font = Font(bold=True, size=16)
        title_cell.alignment = Alignment(horizontal='center')
        title_cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        title_cell.font = Font(bold=True, size=16, color="FFFFFF")
        
        # Add section headers (row 2)
        section_headers = ["GROUPS", "", "", "TEACHERS", "", "", "ROOMS", ""]
        section_colors = ["9BC2E6", "", "", "A9D08E", "", "", "FFD966", ""]
        
        for i, header in enumerate(section_headers):
            cell = index.cell(row=2, column=i+1)
            cell.value = header
            if header:  # Only style non-empty headers
                cell.font = Font(bold=True, size=12)
                cell.alignment = Alignment(horizontal='center')
                cell.fill = PatternFill(start_color=section_colors[i], end_color=section_colors[i], fill_type="solid")
        
        # Add column headers for each section (row 3)
        col_headers = ["Group Name", "Week", "", "Teacher Name", "Week", "", "Room Name", "Week"]
        
        for i, header in enumerate(col_headers):
            cell = index.cell(row=3, column=i+1)
            cell.value = header
            if header:  # Only style non-empty headers
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
                cell.fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
                cell.border = thin_border
        
        # Sort entries by name and then by week
        for category in ['Groups', 'Teachers', 'Rooms']:
            sheet_info[category].sort(key=lambda x: (x['name'], x['week']))
        
        # Add entries for groups
        row = 4
        for entry in sheet_info['Groups']:
            index.cell(row=row, column=1).value = entry['name']
            index.cell(row=row, column=1).alignment = Alignment(horizontal='left', vertical='center')
            index.cell(row=row, column=1).border = thin_border
            
            index.cell(row=row, column=2).value = f"Week {entry['week']}"
            index.cell(row=row, column=2).alignment = Alignment(horizontal='center', vertical='center')
            index.cell(row=row, column=2).border = thin_border
            
            # Add hyperlink to the sheet
            index.cell(row=row, column=1).hyperlink = f"#{entry['sheet_name']}!A1"
            index.cell(row=row, column=1).font = Font(color="0563C1", underline="single")
            row += 1
        
        # Add entries for teachers (start at the same row as groups)
        row = 4
        for entry in sheet_info['Teachers']:
            index.cell(row=row, column=4).value = entry['name']
            index.cell(row=row, column=4).alignment = Alignment(horizontal='left', vertical='center')
            index.cell(row=row, column=4).border = thin_border
            
            index.cell(row=row, column=5).value = f"Week {entry['week']}"
            index.cell(row=row, column=5).alignment = Alignment(horizontal='center', vertical='center')
            index.cell(row=row, column=5).border = thin_border
            
            # Add hyperlink to the sheet
            index.cell(row=row, column=4).hyperlink = f"#{entry['sheet_name']}!A1"
            index.cell(row=row, column=4).font = Font(color="0563C1", underline="single")
            row += 1
        
        # Add entries for rooms (start at the same row as groups)
        row = 4
        for entry in sheet_info['Rooms']:
            index.cell(row=row, column=7).value = entry['name']
            index.cell(row=row, column=7).alignment = Alignment(horizontal='left', vertical='center')
            index.cell(row=row, column=7).border = thin_border
            
            index.cell(row=row, column=8).value = f"Week {entry['week']}"
            index.cell(row=row, column=8).alignment = Alignment(horizontal='center', vertical='center')
            index.cell(row=row, column=8).border = thin_border
            
            # Add hyperlink to the sheet
            index.cell(row=row, column=7).hyperlink = f"#{entry['sheet_name']}!A1"
            index.cell(row=row, column=7).font = Font(color="0563C1", underline="single")
            row += 1
        
        # Add instructions at the bottom
        max_row = max(
            4 + len(sheet_info['Groups']),
            4 + len(sheet_info['Teachers']),
            4 + len(sheet_info['Rooms'])
        ) + 2
        
        index.merge_cells(f'A{max_row}:H{max_row}')
        index.cell(row=max_row, column=1).value = "Click on any name to view the corresponding timetable"
        index.cell(row=max_row, column=1).font = Font(italic=True)
        index.cell(row=max_row, column=1).alignment = Alignment(horizontal='center')
        
        # Add university name and generation date
        max_row += 2
        index.merge_cells(f'A{max_row}:H{max_row}')
        generation_date = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
        index.cell(row=max_row, column=1).value = f"{self.university.name} - Generated on {generation_date}"
        index.cell(row=max_row, column=1).font = Font(italic=True)
        index.cell(row=max_row, column=1).alignment = Alignment(horizontal='center')
        
        # Save the workbook
        wb.save(output_path)
        print(f"Visual timetable saved to {output_path}")