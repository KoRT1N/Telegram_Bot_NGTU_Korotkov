import re

GREETING = re.compile(r"^(привет|здравствуй|добрый день|здравствуйте)$", re.IGNORECASE)
FAREWELL = re.compile(r"^(пока|до свидания)$", re.IGNORECASE)
SET_NAME = re.compile(r"меня зовут ([а-яА-Яa-zA-Z]+)", re.IGNORECASE)

# Математика
ADDITION = re.compile(r"(\d+\.?\d*)\s*\+\s*(\d+\.?\d*)")
SUBTRACTION = re.compile(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)")
MULTIPLICATION = re.compile(r"(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)")
DIVISION = re.compile(r"(\d+\.?\d*)\s*/\s*(\d+\.?\d*)")

TIME_QUERY = re.compile(r"(сколько|какое)\s+время", re.IGNORECASE)
HOW_ARE_YOU = re.compile(r"как\s+(?:у\s+тебя\s+)?дела", re.IGNORECASE)