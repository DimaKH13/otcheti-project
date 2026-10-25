import datetime
import pytest
from src.utils import get_greeting

@pytest.mark.parametrize("time, expected", [
    (datetime.datetime(2023, 1, 1, 7, 0), "Доброе утро"),
    (datetime.datetime(2023, 1, 1, 13, 0), "Добрый день"),
    (datetime.datetime(2023, 1, 1, 20, 0), "Добрый вечер"),
    (datetime.datetime(2023, 1, 1, 2, 0), "Доброй ночи"),
])
def test_get_greeting(time, expected):
    assert get_greeting(time) == expected