import pandas as pd
import pytest
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday

@pytest.fixture
def sample_transactions():
    data = {
        'Дата операции': pd.to_datetime(['2021-12-30 10:00:00', '2021-12-31 15:30:00', 
                                         '2021-10-01 12:00:00', '2021-01-01 10:00:00']),
        'Сумма операции': [-100, -200, -150, -50],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Переводы', 'Супермаркеты']
    }
    return pd.DataFrame(data)

def test_spending_by_category(sample_transactions):
    result = spending_by_category(sample_transactions, 'Супермаркеты', '2021-12-31')
    assert not result.empty
    assert result['Сумма'].iloc[0] == 300

def test_spending_by_weekday(sample_transactions):
    result = spending_by_weekday(sample_transactions, '2021-12-31')
    assert not result.empty
    assert 'День недели' in result.columns

def test_spending_by_workday(sample_transactions):
    result = spending_by_workday(sample_transactions, '2021-12-31')
    assert not result.empty
    assert 'Тип дня' in result.columns