from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardRemove
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
)

from config import config


def start_keyboard_markup(is_admin:bool) -> ReplyKeyboardMarkup:
    """
    Билдер стандартной клавиатуры.

    Returns:
        ReplyKeyboardMarkup: разметка для стандартной клавиатуры
    """
    builder = ReplyKeyboardBuilder()
    mode_text = "👤 Режим пользователя" if is_admin else "⚠️ Режим админа"
    builder.row(
        KeyboardButton(text=mode_text),
    )
    builder.row(
        KeyboardButton(text="🌍 Перейти на сайт"),
        KeyboardButton(text="🤖 О боте"),
    )
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Выберите пункт"
    )

def keyboard_remove():
    return ReplyKeyboardRemove(remove_keyboard=True)


def go_to_web_keyboard_markup() -> InlineKeyboardMarkup:
    """
    Билдер inline клавиатуры для отправки ссылки на сайт системы.

    Returns:
        ReplyKeyboardMarkup: разметка для inline клавиатуры
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти на сайт", url=config.web_url))
    return builder.as_markup()


def votes_keyboard_markup() -> InlineKeyboardMarkup:
    """
    Билдер inline клавиатуры для оценки ответа.

    Returns:
        ReplyKeyboardMarkup: разметка для inline клавиатуры
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👍", callback_data="voted_up"),
        InlineKeyboardButton(text="👎", callback_data="voted_down"),
    )
    return builder.as_markup()
