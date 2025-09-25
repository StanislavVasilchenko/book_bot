from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsDigitCallbackData(BaseFilter):
    """
    Фильтр проверяет что callbackdata состоит только из цифр.
    Нажата кнопка с номером страницы на которую нужно перейти
    """

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.isdigit()


class IsDelBookmarksCallbackData(BaseFilter):
    """Фильтр для удаления номера закладки"""

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.endswith("del") and callback.data[:3].isdigit()
