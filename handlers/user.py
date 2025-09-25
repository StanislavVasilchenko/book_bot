from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon import LEXICON
from keyboards.pagination_kb import create_pagination_keyboard
from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from filters.filters import IsDigitCallbackData, IsDelBookmarksCallbackData


user_router = Router()


@user_router.message(CommandStart())
async def proces_start_command(message: Message, db: dict):
    """
    Команда start
    добавляет пользователя в БД, если его еще нет и
    отправляет приветственное сообщение
    """
    await message.answer(LEXICON[message.text])
    if message.from_user.id not in db:
        db["users"][message.from_user.id] = deepcopy(db.get("user_template"))


@user_router.message(Command(commands=["help"]))
async def proces_help_command(message: Message):
    """
    Отправляет список доступных команд
    :param message:
    """
    await message.answer(LEXICON[message.text])


@user_router.message(Command(commands=["beginning"]))
async def proces_beginning_command(message: Message, db: dict, book: dict):
    """
    Отправляет пользователю первую страницу книги с пагинацией
    :param message:
    :param db:
    :param book:
    """
    db["users"][message.from_user.id]["page"] = 1
    text = book[1]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"1/{len(book)}",
            "forward",
        ),
    )


@user_router.message(Command(commands=["continue"]))
async def proces_continue_command(message: Message, db: dict, book: dict):
    """
    Отправляет пользователю страницу книги на которой
    пользователь остановился в прошлый раз
    """
    text = book[db["users"][message.from_user.id]["page"]]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][message.from_user.id]['page']}/{len(book)}",
            "forward",
        ),
    )


@user_router.message(Command(commands=["bookmarks"]))
async def proces_bookmarks_command(message: Message, db: dict, book: dict):
    """
    Отправляет пользователю список сохраненных закладок или
    сообщение, что закладок нет
    :param message:
    :param db:
    :param book:
    :return:
    """
    if db["users"][message.from_user.id]["bookmarks"]:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *db["users"][message.from_user.id]["bookmarks"],
                book=book,
            ),
        )
    else:
        await message.answer(
            text=LEXICON["no_bookmarks"],
        )


@user_router.callback_query(F.data == "forward")
async def proces_forward_press(callback: CallbackQuery, db: dict, book: dict):
    """
    Срабатывает при нажатии инлайн-кнопки вперед
    :param callback:
    :param db:
    :param book:
    :return:
    """
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page < len(book):
        db["users"][callback.from_user.id]["page"] += 1
        text = book[current_page + 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page + 1}/{len(book)}",
                "forward",
            ),
        )
    await callback.answer()


@user_router.callback_query(F.data == "backward")
async def proces_backward_press(callback: CallbackQuery, db: dict, book: dict):
    """

    :param callback:
    :param db:
    :param book:
    :return:
    """
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page > 1:
        db["users"][callback.from_user.id]["page"] -= 1
        text = book[current_page - 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page - 1}/{len(book)}",
                "forward",
            ),
        )
    await callback.answer()


@user_router.callback_query(
    lambda x: "/" in x.data and x.data.replace("/", "").isdigit(),
)
async def process_page_press(callback: CallbackQuery, db: dict):
    """
    Нажатие инлайн-кнопки с номером текущей страницы
    и добавлять текущую страницу в закладки
    :param callback:
    :param db:
    :return:
    """
    db["users"][callback.from_user.id]["bookmarks"].add(
        db["users"][callback.from_user.id]["page"],
    )
    await callback.answer(text="Страница добавлена в закладки")


@user_router.callback_query(IsDigitCallbackData())
async def process_bookmarks_press(callback: CallbackQuery, db: dict, book: dict):
    """
    Нажатие инлайн-кнопки с закладкой из списка закладок
    :param callback:
    :param db:
    :param book:
    :return:
    """

    text = book[int(callback.data)]
    db["users"][callback.from_user.id]["page"] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][callback.from_user.id]["page"]}/{len(book)}",
            "forward",
        ),
    )


@user_router.callback_query(F.data == "edit_bookmarks")
async def process_edit_press(callback: CallbackQuery, db: dict, book: dict):
    """
    Срабатывает на кнопку "Редактировать", под списком закладок
    :param callback:
    :param db:
    :param book:
    :return:
    """
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *db["users"][callback.from_user.id]["bookmarks"],
            book=book,
        ),
    )


@user_router.callback_query(F.data == "cancel")
async def process_cancel_press(callback: CallbackQuery):
    """
    Нажатие "отменить" во время работы с закладками (просмотр, редактирование)
    :param callback:
    :return:
    """
    await callback.message.edit_text(
        text=LEXICON["cancel_text"],
    )


@user_router.callback_query(IsDelBookmarksCallbackData())
async def process_del_bookmarks_press(callback: CallbackQuery, db: dict, book: dict):
    """
    Удаление закладки из списка закладок
    :param callback:
    :param db:
    :param book:
    :return:
    """
    db["users"][callback.from_user.id]["bookmarks"].remove(int(callback.data[:-3]))
    if db["users"][callback.from_user.id]["bookmarks"]:
        await callback.message.edit_text(
            text=LEXICON["/bookmarks"],
            reply_markup=create_edit_keyboard(
                *db["users"][callback.from_user.id]["bookmarks"],
                book=book,
            ),
        )
    else:
        await callback.message.edit_text(
            text=LEXICON["no_bookmarks"],
        )
