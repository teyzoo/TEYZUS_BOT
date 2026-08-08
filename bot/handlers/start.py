from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import settings
from database.repositories import get_or_create_user
from database.session import async_session_factory
from services.referrals import parse_referral_parameter
from bot.keyboards.main import main_menu_keyboard


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:

    telegram_user = message.from_user

    if telegram_user is None:
        return

    args = message.text.split(maxsplit=1)

    start_parameter = args[1] if len(args) > 1 else None

    referral_code = parse_referral_parameter(
        start_parameter
    )

    referred_by = None

    async with async_session_factory() as session:

        user, created = await get_or_create_user(
            session=session,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language=telegram_user.language_code or "ru",
            referred_by=referred_by,
        )

        if (
            telegram_user.id == settings.owner_id
            and user.role != "owner"
        ):
            user.role = "owner"
            await session.commit()

    if created:
        text = (
            "🚀 <b>Добро пожаловать в TEYZUS!</b>\n\n"
            "Ты успешно зарегистрирован в системе.\n\n"
            "TEYZUS — платформа для поиска, "
            "анализа и работы с Telegram username.\n\n"
            "Выбери нужный раздел:"
        )
    else:
        text = (
            "🚀 <b>С возвращением в TEYZUS!</b>\n\n"
            "Выбери нужный раздел:"
        )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
