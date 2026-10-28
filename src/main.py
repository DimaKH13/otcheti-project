import os
from src.services import read_transactions_excel, search_transactions
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.views import get_main_page_data

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

        print("\n=== Тест поиска (запрос: 'Колхоз') ===")
        search_result = search_transactions(df, "Колхоз")
        print(search_result[:200] + "...")
        
        print("\n=== Данные для главной страницы (JSON) ===")
        # Вот эта строчка теперь стоит ровно!
        print(get_main_page_data(df, date="2021-12-31"))