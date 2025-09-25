import logging
import os

logger = logging.getLogger(__name__)

SYMBOLS = (
    ".",
    ",",
    ":",
    ";",
    "!",
    "?",
)


def _get_part_text(text: str, start: int, size: int):
    if len(text[start : start + size]) < size:
        return text[start : start + size], len(text[start : start + size])
    while (
        text[start : start + size][-1] in SYMBOLS
        and text[start : start + size + 1][-1] in SYMBOLS
        or text[start : start + size][-1] not in SYMBOLS
    ):
        size -= 1
    return text[start : start + size], len(text[start : start + size])


def prepare_book(path: str, page_size: int = 1050) -> dict[int, str]:
    """Функция, формирующая словарь книги"""
    book = {}
    count = 1
    start = 0
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    while True:
        page_text, lenght = _get_part_text(text, start, page_size)
        if not page_text:
            break

        book[count] = page_text.lstrip()
        count += 1
        start += lenght
    return book
