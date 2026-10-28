import pandas as pd
import logging
import json
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def read_transactions_excel(file_path: str) -> Optional[pd.DataFrame]:
    try:
        logger.info(f"Чтение файла: {file_path}")
        df = pd.read_excel(file_path)
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
        return df
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return None

def search_transactions(transactions: pd.DataFrame, query: str) -> str:
    if not query:
        return json.dumps([])
    mask = transactions['Категория'].str.contains(query, case=False, na=False) | \
           transactions['Описание'].str.contains(query, case=False, na=False)
    return transactions[mask].to_json(orient='records', force_ascii=False)

def get_card_info(df: pd.DataFrame) -> list[dict]:
    """Информация по картам."""
    if 'Номер карты' not in df.columns:
        return []
    df_cards = df.dropna(subset=['Номер карты']).copy()
    spends = df_cards[df_cards['Сумма операции'] < 0]
    
    grouped = spends.groupby('Номер карты').agg(
        total_spent=('Сумма операции', lambda x: abs(x.sum()))
    ).reset_index()
    
    result = []
    for _, row in grouped.iterrows():
        card_num = str(row['Номер карты']).replace('*', '')[-4:]
        spent = round(float(row['total_spent']), 2)
        # ПУНКТ 2: Кэшбэк считается как 1% от общей суммы расходов
        cashback = round(spent * 0.01, 2) 
        result.append({
            "last_digits": card_num,
            "total_spent": spent,
            "cashback": cashback
        })
    return result

def get_top_transactions(df: pd.DataFrame, top_n: int = 5) -> list[dict]:
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
    """ПУНКТ 3: Получение курсов валют через внешний API (ЦБ РФ)."""
    logger.info("Запрос курсов валют через API...")
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        data = response.json()['Valute']
        
        result = []
        for c in currencies:
            if c in data:
                result.append({"currency": c, "rate": round(data[c]['Value'], 2)})
            else:
                result.append({"currency": c, "rate": 0.0})
        return result
    except Exception as e:
        logger.error(f"Ошибка API валют: {e}")
        return [{"currency": c, "rate": 0.0} for c in currencies]

def get_stock_prices(stocks: list[str]) -> list[dict]:
    """ПУНКТ 3: Получение цен акций через внешний API (Yahoo Finance)."""
    logger.info("Запрос цен акций через API...")
    result = []
    for s in stocks:
        try:
            # Используем публичный эндпоинт Yahoo Finance
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?interval=1d"
            headers = {"User-Agent": "Mozilla/5.0"} # Чтобы Yahoo не блокировал запрос
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            result.append({"stock": s, "price": round(float(price), 2)})
        except Exception as e:
            logger.error(f"Ошибка API акций {s}: {e}")
            result.append({"stock": s, "price": 0.0})
    return result