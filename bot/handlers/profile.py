from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories import get_user
from database.session import async_session_factory
from services.premium import premium_status_text
from bot.keyboards.main import profile_keyboard


router = Router()


@router.callback_query(F.data == "profile")
async def profile_callback(
    callback: CallbackQuery,
) -> None:

    await callback.answer()

    telegram_user = callback.from_user

    async with async_session_factory() as session:

        user = await get_user(
            session=session,
            telegram_id=telegram_user.id,
        )

    if user is None:
        await callback.message.edit_text(
            "❌ Профиль не найден.\n"
            "Используй /start.",
        )
        return

    username = (
        f"@{user.username}"
        if user.username
        else "не установлен"
    )

    text = (
        "👤 <b>ТВОЙ ПРОФИЛЬ</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"👤 Username: {username}\n"
        f"💎 {premium_status_text(user)}\n\n"
        f"🔎 Успешных поисков сегодня: "
        f"{user.successful_searches_today}\n\n"
        f"💰 Баланс: {user.balance_rub} ₽\n"
        f"⭐ Stars: {user.stars_balance}\n\n"
        f"🎭 Роль: {user.role}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(),
        parse_mode="HTML",
    )
