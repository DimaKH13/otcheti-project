import pandas as pd
from unittest.mock import patch
from src.views import get_main_page_data

@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
def test_get_main_page_data(mock_stocks, mock_currencies):
    mock_currencies.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 175.0}]
    
    df = pd.DataFrame({
        'Номер карты': ['*1234'],
        'Сумма операции': [-100.0],
        'Кэшбэк': [1.0],
        'Дата операции': pd.to_datetime(['2023-01-15']), # Середина месяца
        'Категория': ['Супермаркеты'],
        'Описание': ['Магнит']
    })
    
    # Передаем дату, чтобы проверить фильтрацию
    result_json = get_main_page_data(df, date="2023-01-20")
    
    assert "USD" in result_json
    assert "AAPL" in result_json
    assert "last_digits" in result_json