from aiogram import F, Router
from aiogram.types import CallbackQuery


router = Router()


@router.callback_query(F.data == "search")
async def search_callback(callback: CallbackQuery) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🔎 <b>Поиск username</b>\n\n"
        "Здесь будет полноценный TEYZUS Hunter.\n\n"
        "Система будет сама искать красивые, "
        "редкие, дорогие и перспективные username.\n\n"
        "🔤 5 символов\n"
        "🔤 6+ символов\n"
        "📖 Словарь\n"
        "⚙️ Фильтры\n"
        "🤖 AI-анализ\n"
        "🚨 Ловушки",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "premium")
async def premium_callback(callback: CallbackQuery) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "💎 <b>TEYZUS Premium</b>\n\n"
        "♾ Безлимитный поиск\n"
        "🔤 Поиск от 5 символов\n"
        "📖 Dictionary\n"
        "⚙️ Расширенные фильтры\n"
        "🚨 Ловушки\n"
        "📊 Расширенный AI\n\n"
        "Раздел Premium будет подключён "
        "к полноценной системе оплаты.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "marketplace")
async def marketplace_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "🏪 <b>TEYZUS Marketplace</b>\n\n"
        "Здесь будет полноценный рынок Telegram username.\n\n"
        "🔥 Популярные\n"
        "🆕 Новые\n"
        "💎 Премиум\n"
        "📈 Растущие\n\n"
        "Marketplace будет работать через Mini App.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "referrals")
async def referrals_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "👥 <b>Реферальная система</b>\n\n"
        "Твоя реферальная статистика "
        "будет отображаться здесь.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "support")
async def support_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    await callback.message.edit_text(
        "💬 <b>Поддержка TEYZUS</b>\n\n"
        "Раздел поддержки будет подключён "
        "к полноценной системе обращений.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(
    callback: CallbackQuery,
) -> None:

    from bot.keyboards.main import main_menu_keyboard

    await callback.answer()

    await callback.message.edit_text(
        "🚀 <b>TEYZUS</b>\n\n"
        "Выбери нужный раздел:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
