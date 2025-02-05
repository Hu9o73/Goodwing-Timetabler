import pandas as pd

def createCSV(xlsx_path: str = './GoodwingTimetabler/UniversityInstance/UniversityGenerator.xlsx'):
    sheets = ['University', 'Promotions', 'Subjects']
    dfs = []
    for idx, sheet_name in enumerate(sheets):
        dfs.append(pd.read_excel(xlsx_path, sheet_name))
        dfs[idx].to_csv(f'./GoodwingTimetabler/UniversityInstance/{sheet_name}.csv', index=False)

    for df in dfs:
        print(dfs)
