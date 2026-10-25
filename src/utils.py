import datetime
from typing import Optional

def get_greeting(current_time: Optional[datetime.datetime] = None) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    if current_time is None:
        current_time = datetime.datetime.now()
    
    hour = current_time.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"