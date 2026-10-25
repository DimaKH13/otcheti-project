import pandas as pd
from unittest.mock import patch
from src.views import get_main_page_data

@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_get_main_page_data(mock_stocks, mock_currencies):
    # Настраиваем моки (что они должны вернуть при вызове)
    mock_currencies.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 175.0}]
    
    df = pd.DataFrame({
        'Номер карты': ['*1234'],
        'Сумма операции': [-100.0],
        'Кэшбэк': [1.0],
        'Дата операции': pd.to_datetime(['2023-01-01']),
        'Категория': ['Супермаркеты'],
        'Описание': ['Магнит']
    })
    
    # Вызываем функцию
    result_json = get_main_page_data(df)
    
    # Проверяем, что в итоговом JSON есть наши замоканные данные
    assert "USD" in result_json
    assert "AAPL" in result_json
    assert "last_digits" in result_json