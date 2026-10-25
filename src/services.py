import pandas as pd
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_transactions_excel(file_path: str) -> Optional[pd.DataFrame]:
    """Читает транзакции из Excel-файла."""
    try:
        logger.info(f"Чтение файла: {file_path}")
        df = pd.read_excel(file_path)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
        return df
    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return None

def search_transactions(transactions: pd.DataFrame, query: str) -> str:
    """Поиск транзакций по подстроке в описании или категории (без учета регистра)."""
    logger.info(f"Поиск по запросу: {query}")
    if not query:
        return json.dumps([])
        
    mask = transactions['Категория'].str.contains(query, case=False, na=False) | \
           transactions['Описание'].str.contains(query, case=False, na=False)
           
    result_df = transactions[mask]
    return result_df.to_json(orient='records', force_ascii=False)

def get_card_info(df: pd.DataFrame) -> list[dict]:
    """Информация по картам (сумма расходов, кэшбэк)."""
    if 'Номер карты' not in df.columns:
        return []
    
    df_cards = df.dropna(subset=['Номер карты']).copy()
    spends = df_cards[df_cards['Сумма операции'] < 0]
    
    grouped = spends.groupby('Номер карты').agg(
        total_spent=('Сумма операции', lambda x: abs(x.sum())),
        total_cashback=('Кэшбэк', 'sum')
    ).reset_index()
    
    result = []
    for _, row in grouped.iterrows():
        card_num = str(row['Номер карты']).replace('*', '')[-4:]
        result.append({
            "last_digits": card_num,
            "total_spent": round(float(row['total_spent']), 2),
            "cashback": round(float(row['total_cashback']), 2)
        })
    return result

def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> list[dict]:
    """Топ-N транзакций по сумме платежа."""
    spends = df[df['Сумма операции'] < 0].copy()
    spends['abs_amount'] = spends['Сумма операции'].abs()
    top_df = spends.sort_values(by='abs_amount', ascending=False).head(top_n)
    
    result = []
    for _, row in top_df.iterrows():
        result.append({
            "date": row['Дата операции'].strftime('%d.%m.%Y'),
            "amount": round(float(row['Сумма операции']), 2),
            "category": row['Категория'] if pd.notna(row['Категория']) else "",
            "description": row['Описание'] if pd.notna(row['Описание']) else ""
        })
    return result

def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Заглушка для получения курсов валют (по ТЗ)."""
    rates = {"USD": 90.0, "EUR": 100.0, "GBP": 115.0}
    return [{"currency": c, "rate": rates.get(c, 0.0)} for c in currencies]

def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Заглушка для получения цен акций (по ТЗ)."""
    prices = {"AAPL": 175.0, "MSFT": 330.0, "GOOGL": 140.0}
    return [{"stock": s, "price": prices.get(s, 0.0)} for s in stocks]