import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import settings
from database.repositories import get_user
from database.session import async_session_factory
from services.hunter.engine import HunterEngine
from services.premium import is_premium

from bot.keyboards.main import (
    main_menu_keyboard,
    search_back_keyboard,
    search_keyboard,
)


router = Router()

logger = logging.getLogger("TEYZUS.menu")

hunter = HunterEngine()


@router.callback_query(F.data == "search")
async def search_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🔎 <b>TEYZUS HUNTER</b>\n\n"
        "Ты не вводишь конкретный username.\n\n"
        "TEYZUS сам ищет красивые, редкие, "
        "дорогие и перспективные username.\n\n"
        "Выбери тип поиска:",
        reply_markup=search_keyboard(),
        parse_mode="HTML",
    )


async def run_hunter(
    callback: CallbackQuery,
    length: int,
    title: str,
    amount: int = 5,
) -> None:

    await callback.answer()

    async with async_session_factory() as session:

        user = await get_user(
            session=session,
            telegram_id=callback.from_user.id,
        )

    if user is None:
        await callback.message.edit_text(
            "❌ Профиль не найден.\n"
            "Используй /start.",
        )
        return

    if length < settings.free_search_length:

        if not is_premium(user):
            await callback.message.edit_text(
                "💎 <b>Этот поиск доступен только Premium.</b>\n\n"
                "Username из 5 символов доступны "
                "в TEYZUS Premium.",
                parse_mode="HTML",
                reply_markup=search_back_keyboard(),
            )
            return

    if (
        not is_premium(user)
        and user.successful_searches_today
        >= settings.free_daily_limit
    ):
        await callback.message.edit_text(
            "⛔️ <b>Дневной лимит исчерпан.</b>\n\n"
            "Free-пользователь получает "
            f"{settings.free_daily_limit} успешных "
            "найденных username в день.\n\n"
            "💎 Premium — безлимитный поиск.",
            parse_mode="HTML",
            reply_markup=search_back_keyboard(),
        )
        return

    await callback.message.edit_text(
        f"🔎 <b>{title}</b>\n\n"
        "Генерирую красивые кандидаты...\n"
        "Проверяю структуру...\n"
        "Отбрасываю случайный набор букв...\n"
        "Запускаю проверки доступности...\n\n"
        "⏳ Пожалуйста, подожди.",
        parse_mode="HTML",
    )

    try:
        results = await hunter.search(
            length=length,
            amount=amount,
        )

    except Exception:
        logger.exception(
            "Hunter search failed"
        )

        await callback.message.edit_text(
            "❌ Во время поиска произошла ошибка.\n\n"
            "Попробуй ещё раз позже.",
            reply_markup=search_back_keyboard(),
        )

        return

    if not results:
        await callback.message.edit_text(
            "😔 <b>Подходящих свободных username "
            "не найдено.</b>\n\n"
            "Попробуй другой тип поиска.",
            parse_mode="HTML",
            reply_markup=search_back_keyboard(),
        )

        return

    lines = [
        "✨ <b>TEYZUS — НАЙДЕННЫЕ USERNAME</b>",
        "",
    ]

    for index, result in enumerate(
        results,
        start=1,
    ):

        lines.extend(
            [
                f"<b>{index}. @{result.username}</b>",
                f"🤖 AI Score: {result.beauty_score}/10",
                f"📖 Читабельность: {result.readability}/10",
                f"💎 Редкость: {result.rarity}/10",
                f"🏷 Брендовость: {result.brand}/10",
                f"📈 Ликвидность: {result.liquidity}/10",
                f"💰 Оценка: ${result.price_min:,}–${result.price_max:,}",
                "⚡️ Свободен",
                "",
            ]
        )

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=search_back_keyboard(),
    )


@router.callback_query(F.data == "hunter_6")
async def hunter_6_callback(
    callback: CallbackQuery,
) -> None:

    await run_hunter(
        callback=callback,
        length=6,
        title="✨ КРАСИВЫЕ 6 БУКВ",
    )


@router.callback_query(F.data == "hunter_expensive_6")
async def hunter_expensive_6_callback(
    callback: CallbackQuery,
) -> None:

    await run_hunter(
        callback=callback,
        length=6,
        title="💎 ДОРОГИЕ 6 БУКВ",
        amount=5,
    )


@router.callback_query(F.data == "hunter_dictionary")
async def hunter_dictionary_callback(
    callback: CallbackQuery,
) -> None:

    await run_hunter(
        callback=callback,
        length=6,
        title="📖 СЛОВАРНЫЕ USERNAME",
        amount=5,
    )


@router.callback_query(F.data == "hunter_popular")
async def hunter_popular_callback(
    callback: CallbackQuery,
) -> None:

    await run_hunter(
        callback=callback,
        length=6,
        title="🔥 ПОПУЛЯРНЫЕ USERNAME",
        amount=5,
    )


@router.callback_query(F.data == "hunter_5")
async def hunter_5_callback(
    callback: CallbackQuery,
) -> None:

    await run_hunter(
        callback=callback,
        length=5,
        title="🔤 5 БУКВ — PREMIUM",
        amount=5,
    )


@router.callback_query(F.data == "hunter_mask")
async def hunter_mask_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🎯 <b>ПОИСК ПО МАСКЕ</b>\n\n"
        "Система масок будет подключена "
        "в следующем модуле Hunter.\n\n"
        "Примеры:\n"
        "<code>a???a?</code>\n"
        "<code>?nova?</code>\n"
        "<code>??ora?</code>",
        parse_mode="HTML",
        reply_markup=search_back_keyboard(),
    )


@router.callback_query(F.data == "premium")
async def premium_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "💎 <b>TEYZUS PREMIUM</b>\n\n"
        "♾ Безлимитный поиск\n"
        "🔤 Username от 5 символов\n"
        "📖 Dictionary\n"
        "⚙️ Расширенные фильтры\n"
        "🚨 Ловушки\n"
        "📊 Расширенный AI\n\n"
        "Система Premium будет подключена "
        "к полноценной платежной системе.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "marketplace")
async def marketplace_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🏪 <b>TEYZUS Marketplace</b>\n\n"
        "Полноценный Marketplace будет работать "
        "через Mini App.\n\n"
        "🔥 Популярные\n"
        "🆕 Новые\n"
        "💎 Premium\n"
        "📈 Растущие",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "referrals")
async def referrals_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "👥 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>\n\n"
        "Полная статистика рефералов "
        "будет подключена следующим модулем.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "support")
async def support_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "💬 <b>ПОДДЕРЖКА TEYZUS</b>\n\n"
        "Система обращений будет подключена "
        "отдельным модулем.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🚀 <b>TEYZUS</b>\n\n"
        "Выбери нужный раздел:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
