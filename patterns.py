import re

GREETING = re.compile(r"^(привет|здравствуй|добрый день|здравствуйте)$", re.IGNORECASE)
FAREWELL = re.compile(r"^(пока|до свидания)$", re.IGNORECASE)
WEATHER = re.compile(r"погода в ([а-яА-Яa-zA-Z\- ]+)", re.IGNORECASE)
SET_NAME = re.compile(r"меня зовут ([а-яА-Яa-zA-Z]+)", re.IGNORECASE)

ADDITION = re.compile(r"(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)")
SUBTRACTION = re.compile(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)")
MULTIPLICATION = re.compile(r"(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)")
DIVISION = re.compile(r"(\d+\.?\d*)\s*/\s*(\d+\.?\d*)")

TIME_QUERY = re.compile(r"(сколько|какое) время", re.IGNORECASE)
HOW_ARE_YOU = re.compile(r"как (у тебя )?дела", re.IGNORECASE)