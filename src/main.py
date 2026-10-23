import os
from src.services import read_transactions_excel
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday

if __name__ == "__main__":
    file_path = os.path.join("data", "operations.xlsx")
    df = read_transactions_excel(file_path)
    
    if df is not None:
        print("=== Траты по категории 'Супермаркеты' ===")
        print(spending_by_category(df, "Супермаркеты", "2021-12-31"))
        
        print("\n=== Средние траты по дням недели ===")
        print(spending_by_weekday(df, "2021-12-31"))
        
        print("\n=== Средние траты в рабочий/выходной день ===")
        print(spending_by_workday(df, "2021-12-31"))