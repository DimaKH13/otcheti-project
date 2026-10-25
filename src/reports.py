import pandas as pd
import datetime
import logging
import json
import functools
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

# --- ОБЪЕДИНЕННЫЙ ДЕКОРАТОР  ---
def save_report(filename: Optional[str] = None) -> Callable:
    """Декоратор для сохранения отчета. Может использоваться с параметром и без."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            # Если имя файла не передано, генерируем его по названию функции
            out_file = filename if filename else f"{func.__name__}_default.json"
            try:
                with open(out_file, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
                logger.info(f"Отчет сохранен в {out_file}")
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")
            return result
        return wrapper
    
    # Проверка: если декоратор вызван без скобок (@save_report)
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)
    
    return decorator

def _filter_last_3_months(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    if date:
        end_date = pd.to_datetime(date)
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

# --- ОТЧЕТЫ ---

@save_report
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    df_filtered = df[df['Категория'] == category]
    result = df_filtered.groupby('Категория')['Сумма'].sum().reset_index()
    return result

@save_report
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    
    # ПУНКТ 4: Группируем по дате (дню), чтобы получить сумму трат за каждый конкретный день
    df['Дата'] = df['Дата операции'].dt.date
    daily_spend = df.groupby('Дата')['Сумма'].sum().reset_index()
    
    # Теперь определяем день недели для каждого дня
    weekdays_ru = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    daily_spend['День недели'] = pd.to_datetime(daily_spend['Дата']).dt.day_of_week.map(weekdays_ru)
    
    # Считаем среднее по дням недели
    result = daily_spend.groupby('День недели')['Сумма'].mean().reset_index()
    result['Сумма'] = result['Сумма'].round(2)
    return result

@save_report
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    df = _filter_last_3_months(transactions, date)
    
    # ПУНКТ 4: Также группируем по дням
    df['Дата'] = df['Дата операции'].dt.date
    daily_spend = df.groupby('Дата')['Сумма'].sum().reset_index()
    
    # Определяем тип дня
    daily_spend['Тип дня'] = pd.to_datetime(daily_spend['Дата']).dt.day_of_week.apply(lambda x: 'Рабочий' if x < 5 else 'Выходной')
    
    # Считаем среднее
    result = daily_spend.groupby('Тип дня')['Сумма'].mean().reset_index()
    result['Сумма'] = result['Сумма'].round(2)
    return result