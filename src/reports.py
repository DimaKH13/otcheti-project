import pandas as pd
import datetime
import logging
import json
import functools
from typing import Optional

logger = logging.getLogger(__name__)

def save_report_default(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        filename = f"{func.__name__}_default.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
            logger.info(f"Отчет сохранен в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
        return result
    return wrapper

def save_report_param(filename: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
                logger.info(f"Отчет сохранен в {filename}")
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
            return result
        return wrapper
    return decorator

def _filter_last_3_months(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    if date:
        end_date = pd.to_datetime(date)
        # Если передана только дата (время 00:00:00), включаем весь день до 23:59:59
        if end_date == end_date.normalize():
            end_date = end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    else:
        end_date = pd.Timestamp(datetime.datetime.now())
        
    start_date = end_date - pd.DateOffset(months=3)
    
    df = transactions[
        (transactions['Дата операции'] >= start_date) & 
        (transactions['Дата операции'] <= end_date) &
        (transactions['Сумма операции'] < 0)
    ].copy()
    df['Сумма'] = df['Сумма операции'].abs()
    return df

@save_report_default
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    df_filtered = df[df['Категория'] == category]
    result = df_filtered.groupby('Категория')['Сумма'].sum().reset_index()
    return result

@save_report_default
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    weekdays_ru = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    # Используем day_of_week вместо устаревшего weekday
    df['День недели'] = df['Дата операции'].dt.day_of_week.map(weekdays_ru)
    result = df.groupby('День недели')['Сумма'].mean().reset_index()
    result['Сумма'] = result['Сумма'].round(2)
    return result

@save_report_default
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    # Используем day_of_week вместо устаревшего weekday
    df['Тип дня'] = df['Дата операции'].dt.day_of_week.apply(lambda x: 'Рабочий' if x < 5 else 'Выходной')
    result = df.groupby('Тип дня')['Сумма'].mean().reset_index()
    result['Сумма'] = result['Сумма'].round(2)
    return result