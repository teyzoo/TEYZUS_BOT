from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🔎 Поиск",
            callback_data="search",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="💎 Premium",
            callback_data="premium",
        ),
        InlineKeyboardButton(
            text="🏪 Marketplace",
            callback_data="marketplace",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="👤 Профиль",
            callback_data="profile",
        ),
        InlineKeyboardButton(
            text="👥 Рефералы",
            callback_data="referrals",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="💬 Поддержка",
            callback_data="support",
        ),
    )

    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="💎 Premium",
            callback_data="premium",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="👥 Рефералы",
            callback_data="referrals",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="main_menu",
        ),
    )

    return builder.as_markup()


def search_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✨ Красивые 6 букв",
            callback_data="hunter_6",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="💎 Дорогие 6 букв",
            callback_data="hunter_expensive_6",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="📖 Словарные",
            callback_data="hunter_dictionary",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="🔥 Популярные",
            callback_data="hunter_popular",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="🔤 5 букв — Premium",
            callback_data="hunter_5",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="🎯 По маске",
            callback_data="hunter_mask",
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="main_menu",
        ),
    )

    return builder.as_markup()


def search_back_keyboard() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="search",
        ),
    )

    return builder.as_markup()
