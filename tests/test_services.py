import pandas as pd
from src.services import search_transactions

def test_search_transactions():
    df = pd.DataFrame({
        'Категория': ['Супермаркеты', 'Переводы'],
        'Описание': ['Колхоз', 'Дмитрий Ш.']
    })
    
    # Тест на успешный поиск
    res = search_transactions(df, "колхоз")
    assert "Колхоз" in res
    
    # Тест на поиск, которого нет
    res_empty = search_transactions(df, "Аптека")
    assert res_empty == "[]"