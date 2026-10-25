import json
import logging
from typing import Optional
import pandas as pd
from src.utils import get_greeting
from src.services import get_card_info, get_top_transactions, get_currency_rates, get_stock_prices

logger = logging.getLogger(__name__)

def get_main_page_data(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Формирует JSON-данные для главной страницы."""
    logger.info("Формирование данных для главной страницы")
    
    greeting = get_greeting()
    cards = get_card_info(transactions)
    top_trans = get_top_transactions(transactions, 5)
    
    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        currencies = settings.get("user_currencies", ["USD", "EUR"])
        stocks = settings.get("user_stocks", ["AAPL", "MSFT"])
    except Exception as e:
        logger.error(f"Ошибка чтения настроек: {e}")
        currencies = ["USD", "EUR"]
        stocks = ["AAPL"]
        
    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)
    
    main_data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_trans,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    
    return json.dumps(main_data, ensure_ascii=False, indent=4)