from __future__ import annotations

import asyncio
import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from aiogram import (
    Bot,
    Dispatcher,
    F,
)
from aiogram.client.default import (
    DefaultBotProperties,
)
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from fastapi import FastAPI
import uvicorn

from config import (
    ADMIN_IDS,
    FREE_MIN_USERNAME_LENGTH,
    FREE_SEARCHES_PER_DAY,
    MAX_USERNAME_LENGTH,
    PREMIUM_BATCH_SIZE,
    PREMIUM_MIN_USERNAME_LENGTH,
    PREMIUM_SEARCHES_PER_DAY,
    PORT,
    TRAP_INTERVAL_SECONDS,
)

from database import (
    SessionLocal,
    Trap,
    User,
    create_listing,
    create_promo,
    create_user,
    get_active_traps,
    get_listings,
    get_promo,
    get_user,
    get_user_stats,
    increment_search,
    init_db,
    is_premium if False else None,
    remove_trap,
    reset_daily_counter,
    save_search,
    set_premium,
    update_trap_status,
    use_promo,
    add_trap,
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("TEYZUS")

BOT_TOKEN = __import__("config").BOT_TOKEN

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

dp = Dispatcher()


def keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔎 Найти юзер"
                ),
                KeyboardButton(
                    text="📦 Массовый поиск"
                ),
            ],
            [
                KeyboardButton(
                    text="👤 Профиль"
                ),
                KeyboardButton(
                    text="💎 Premium"
                ),
            ],
            [
                KeyboardButton(
                    text="🪤 Trap"
                ),
                KeyboardButton(
                    text="👥 Рефералы"
                ),
            ],
            [
                KeyboardButton(
                    text="🎟 Промокод"
                ),
                KeyboardButton(
                    text="🛒 Marketplace"
                ),
            ],
        ],
        resize_keyboard=True,
    )


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📊 Статистика"
                ),
                KeyboardButton(
                    text="💎 Выдать Premium"
                ),
            ],
            [
                KeyboardButton(
                    text="🎟 Создать промокод"
                ),
            ],
        ],
        resize_keyboard=True,
    )


def normalize_username(
    text: str,
) -> Optional[str]:
    text = text.strip()

    if text.startswith("@"):
        text = text[1:]

    if not re.fullmatch(
        rf"[A-Za-z0-9_]{{{PREMIUM_MIN_USERNAME_LENGTH},{MAX_USERNAME_LENGTH}}}",
        text,
    ):
        return None

    return text.lower()


def extract_usernames(
    text: str,
) -> list[str]:
    found = re.findall(
        rf"@?[A-Za-z0-9_]{{{PREMIUM_MIN_USERNAME_LENGTH},{MAX_USERNAME_LENGTH}}}",
        text,
    )

    result = []

    for item in found:
        username = normalize_username(item)

        if username and username not in result:
            result.append(username)

    return result


async def telegram_check(
    username: str,
) -> Optional[bool]:
    """
    True  = потенциально свободен
    False = найден/занят
    None  = Telegram не позволил определить статус

    Bot API не предоставляет отдельный официальный
    метод "is username available", поэтому результат
    "свободен" здесь является именно предварительной
    проверкой.
    """

    try:
        await bot.get_chat(
            f"@{username}"
        )

        return False

    except Exception as error:
        message = str(error).lower()

        if (
            "chat not found" in message
            or "username not found" in message
        ):
            return True

        if "bad request" in message:
            return True

        logger.warning(
            "Telegram check failed @%s: %s",
            username,
            error,
        )

        return None


async def ensure_user(
    message: Message,
    referral_id: Optional[int] = None,
):
    if not message.from_user:
        return None

    return await create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referral_id=referral_id,
    )


async def premium_active(
    user: Optional[User],
) -> bool:
    if not user:
        return False

    if not user.is_premium:
        return False

    if (
        user.premium_until
        and user.premium_until
        < datetime.now(timezone.utc)
    ):
        return False

    return True


async def can_search(
    user_id: int,
    username: str,
):
    user = await get_user(user_id)

    if not user:
        return False, "Пользователь не найден."

    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    user = await reset_daily_counter(
        user_id,
        today,
    )

    premium = await premium_active(user)

    minimum = (
        PREMIUM_MIN_USERNAME_LENGTH
        if premium
        else FREE_MIN_USERNAME_LENGTH
    )

    if len(username) < minimum:
        return (
            False,
            (
                f"❌ Минимальная длина "
                f"для тебя: <b>{minimum}</b>."
            ),
        )

    limit = (
        PREMIUM_SEARCHES_PER_DAY
        if premium
        else FREE_SEARCHES_PER_DAY
    )

    if user.searches_today >= limit:
        return (
            False,
            (
                "⛔ Лимит проверок на сегодня "
                "исчерпан.\n\n"
                f"Использовано: "
                f"{user.searches_today}/{limit}"
            ),
        )

    return True, ""


@dp.message(CommandStart())
async def start(
    message: Message,
):
    referral_id = None

    if message.text:
        parts = message.text.split(maxsplit=1)

        if len(parts) == 2:
            payload = parts[1]

            if payload.startswith("ref_"):
                value = payload[4:]

                if value.isdigit():
                    referral_id = int(value)

    await ensure_user(
        message,
        referral_id,
    )

    await message.answer(
        (
            "🚀 <b>TEYZUS</b>\n\n"
            "Поиск и мониторинг "
            "Telegram-юзернеймов.\n\n"
            "🔎 Проверяй username\n"
            "📦 Ищи сразу несколько\n"
            "🪤 Ставь Trap\n"
            "💎 Используй Premium\n"
            "🛒 Просматривай Marketplace\n\n"
            "Выбери действие:"
        ),
        reply_markup=keyboard(),
    )


@dp.message(F.text == "🔎 Найти юзер")
async def search_help(
    message: Message,
):
    await ensure_user(message)

    await message.answer(
        (
            "🔎 <b>ПОИСК USERNAME</b>\n\n"
            "Отправь мне:\n\n"
            "<code>@username</code>\n\n"
            f"🆓 Бесплатно: "
            f"от {FREE_MIN_USERNAME_LENGTH} символов\n"
            f"💎 Premium: "
            f"от {PREMIUM_MIN_USERNAME_LENGTH} символов"
        )
    )


@dp.message(F.text == "📦 Массовый поиск")
async def batch_help(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    if not await premium_active(user):
        await message.answer(
            (
                "💎 <b>Массовый поиск</b>\n\n"
                "Функция доступна Premium.\n\n"
                f"Можно будет проверять "
                f"до {PREMIUM_BATCH_SIZE} "
                "username одновременно."
            )
        )
        return

    await message.answer(
        (
            "📦 <b>МАССОВЫЙ ПОИСК</b>\n\n"
            f"Отправь до {PREMIUM_BATCH_SIZE} "
            "username.\n\n"
            "Например:\n"
            "<code>"
            "@alpha\n"
            "@test\n"
            "@hello"
            "</code>"
        )
    )


@dp.message(F.text == "👤 Профиль")
async def profile(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    searches, traps = await get_user_stats(
        user.id
    )

    premium = await premium_active(user)

    premium_text = (
        "💎 Активен"
        if premium
        else "❌ Нет"
    )

    await message.answer(
        (
            "👤 <b>ТВОЙ ПРОФИЛЬ</b>\n\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"👤 Username: "
            f"@{user.username or 'нет'}\n\n"
            f"💎 Premium: {premium_text}\n"
            f"🔎 Проверок сегодня: "
            f"{user.searches_today}\n"
            f"📊 Всего проверок: "
            f"{searches}\n"
            f"🪤 Активных Trap: "
            f"{traps}\n"
            f"👥 Рефералов: "
            f"{user.referral_count}\n"
            f"💰 Баланс: "
            f"{user.balance:.2f} RUB"
        )
    )


@dp.message(F.text == "💎 Premium")
async def premium(
    message: Message,
):
    await ensure_user(message)

    await message.answer(
        (
            "💎 <b>TEYZUS PREMIUM</b>\n\n"
            "Premium будет включать:\n\n"
            "⚡ повышенный лимит\n"
            "🔤 поиск от 5 символов\n"
            "📦 массовый поиск\n"
            "🪤 Trap\n"
            "🎯 расширенные фильтры\n"
            "📊 расширенная статистика\n\n"
            "Оплата подключается следующим этапом "
            "через Telegram Stars."
        )
    )


@dp.message(F.text == "🪤 Trap")
async def trap_help(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    if not await premium_active(user):
        await message.answer(
            (
                "🪤 <b>TRAP</b>\n\n"
                "Trap доступен только Premium.\n\n"
                "Он позволяет следить за username "
                "и получить уведомление, когда "
                "проверка покажет его как "
                "потенциально свободный."
            )
        )
        return

    await message.answer(
        (
            "🪤 <b>TRAP</b>\n\n"
            "Добавить username:\n"
            "<code>/trap @username</code>\n\n"
            "Удалить:\n"
            "<code>/untrap @username</code>\n\n"
            "Активные Trap:\n"
            "<code>/traps</code>"
        )
    )


@dp.message(F.text.startswith("/trap"))
async def trap_add_handler(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    if not await premium_active(user):
        await message.answer(
            "💎 Trap доступен только Premium."
        )
        return

    parts = (message.text or "").split()

    if len(parts) != 2:
        await message.answer(
            "Используй: <code>/trap @username</code>"
        )
        return

    username = normalize_username(parts[1])

    if not username:
        await message.answer(
            "❌ Некорректный username."
        )
        return

    created = await add_trap(
        user.id,
        username,
    )

    if created:
        await message.answer(
            (
                "🪤 <b>TRAP АКТИВИРОВАН</b>\n\n"
                f"@{username}\n\n"
                "Я буду периодически проверять "
                "его статус."
            )
        )
    else:
        await message.answer(
            "⚠️ Этот Trap уже активен."
        )


@dp.message(F.text.startswith("/untrap"))
async def trap_remove_handler(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    parts = (message.text or "").split()

    if len(parts) != 2:
        await message.answer(
            "Используй: "
            "<code>/untrap @username</code>"
        )
        return

    username = normalize_username(parts[1])

    if not username:
        await message.answer(
            "❌ Некорректный username."
        )
        return

    removed = await remove_trap(
        user.id,
        username,
    )

    await message.answer(
        (
            "✅ Trap удалён."
            if removed
            else "❌ Такой активный Trap не найден."
        )
    )


@dp.message(F.text == "/traps")
async def traps_list(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    if not await premium_active(user):
        await message.answer(
            "💎 Trap доступен только Premium."
        )
        return

    traps = await get_active_traps()

    mine = [
        trap
        for trap in traps
        if trap.user_id == user.id
    ]

    if not mine:
        await message.answer(
            "🪤 У тебя нет активных Trap."
        )
        return

    text = [
        "🪤 <b>ТВОИ TRAP</b>\n"
    ]

    for trap in mine:
        status = (
            "🟢"
            if trap.last_status is True
            else "🔴"
            if trap.last_status is False
            else "⚪"
        )

        text.append(
            f"{status} @{trap.username}"
        )

    await message.answer(
        "\n".join(text)
    )


@dp.message(F.text == "👥 Рефералы")
async def referrals(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    me = await bot.get_me()

    link = (
        f"https://t.me/{me.username}"
        f"?start=ref_{user.id}"
    )

    await message.answer(
        (
            "👥 <b>РЕФЕРАЛЬНАЯ СИСТЕМА</b>\n\n"
            f"Приглашено: "
            f"<b>{user.referral_count}</b>\n\n"
            "Твоя ссылка:\n"
            f"<code>{link}</code>"
        )
    )


@dp.message(F.text == "🎟 Промокод")
async def promo_help(
    message: Message,
):
    await ensure_user(message)

    await message.answer(
        (
            "🎟 <b>ПРОМОКОД</b>\n\n"
            "Отправь:\n"
            "<code>/promo CODE</code>"
        )
    )


@dp.message(F.text.startswith("/promo"))
async def promo_handler(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    parts = (message.text or "").split()

    if len(parts) != 2:
        await message.answer(
            "Используй: <code>/promo CODE</code>"
        )
        return

    code = parts[1].upper()

    promo = await get_promo(code)

    if not promo:
        await message.answer(
            "❌ Промокод не найден."
        )
        return

    success = await use_promo(
        user.id,
        promo.id,
    )

    if success:
        await message.answer(
            (
                "🎉 <b>ПРОМОКОД АКТИВИРОВАН</b>\n\n"
                f"💎 Premium: "
                f"{promo.premium_days} дней"
            )
        )
    else:
        await message.answer(
            "❌ Промокод недействителен "
            "или уже использован."
        )


@dp.message(F.text == "🛒 Marketplace")
async def marketplace(
    message: Message,
):
    await ensure_user(message)

    listings = await get_listings()

    if not listings:
        await message.answer(
            (
                "🛒 <b>MARKETPLACE</b>\n\n"
                "Пока активных объявлений нет.\n\n"
                "Добавить username:\n"
                "<code>/sell @username 5000</code>"
            )
        )
        return

    text = [
        "🛒 <b>TEYZUS MARKETPLACE</b>\n"
    ]

    for item in listings:
        description = (
            f"\n{item.description}"
            if item.description
            else ""
        )

        text.append(
            (
                f"👤 <b>@{item.username}</b>\n"
                f"💰 {item.price:.2f} "
                f"{item.currency}"
                f"{description}\n"
                f"🆔 #{item.id}\n"
            )
        )

    text.append(
        "\nДля покупки используй "
        "<code>/buy ID</code>."
    )

    await message.answer(
        "\n".join(text)
    )


@dp.message(F.text.startswith("/sell"))
async def sell_handler(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    parts = (message.text or "").split(
        maxsplit=3
    )

    if len(parts) < 3:
        await message.answer(
            (
                "Используй:\n"
                "<code>/sell @username 5000</code>\n\n"
                "Описание можно добавить третьим "
                "параметром."
            )
        )
        return

    username = normalize_username(parts[1])

    if not username:
        await message.answer(
            "❌ Некорректный username."
        )
        return

    try:
        price = float(parts[2])
    except ValueError:
        await message.answer(
            "❌ Цена должна быть числом."
        )
        return

    if price <= 0:
        await message.answer(
            "❌ Цена должна быть больше нуля."
        )
        return

    description = (
        parts[3]
        if len(parts) == 4
        else None
    )

    success = await create_listing(
        seller_id=user.id,
        username=username,
        price=price,
        currency="RUB",
        description=description,
    )

    if success:
        await message.answer(
            (
                "✅ <b>Объявление создано</b>\n\n"
                f"@{username}\n"
                f"💰 {price:.2f} RUB"
            )
        )
    else:
        await message.answer(
            "❌ Этот username уже выставлен."
        )


@dp.message(F.text == "📊 Статистика")
async def admin_stats(
    message: Message,
):
    if not message.from_user:
        return

    if message.from_user.id not in ADMIN_IDS:
        return

    async with SessionLocal() as session:
        from sqlalchemy import func, select

        users = await session.execute(
            select(func.count(User.id))
        )

        searches = await session.execute(
            select(func.count())
            .select_from(
                __import__(
                    "database"
                ).SearchHistory
            )
        )

        traps = await session.execute(
            select(func.count())
            .select_from(Trap)
            .where(
                Trap.active == True
            )
        )

    await message.answer(
        (
            "📊 <b>TEYZUS STATISTICS</b>\n\n"
            f"👤 Users: "
            f"{users.scalar() or 0}\n"
            f"🔎 Searches: "
            f"{searches.scalar() or 0}\n"
            f"🪤 Active traps: "
            f"{traps.scalar() or 0}"
        ),
        reply_markup=admin_keyboard(),
    )


@dp.message(F.text.startswith("/premium"))
async def admin_premium(
    message: Message,
):
    if not message.from_user:
        return

    if message.from_user.id not in ADMIN_IDS:
        return

    parts = (message.text or "").split()

    if len(parts) != 3:
        await message.answer(
            (
                "Используй:\n"
                "<code>/premium USER_ID DAYS</code>"
            )
        )
        return

    try:
        target_id = int(parts[1])
        days = int(parts[2])
    except ValueError:
        await message.answer(
            "❌ USER_ID и DAYS должны быть числами."
        )
        return

    if days <= 0:
        await message.answer(
            "❌ Количество дней должно быть > 0."
        )
        return

    target = await get_user(target_id)

    if not target:
        await message.answer(
            "❌ Пользователь не найден."
        )
        return

    now = datetime.now(timezone.utc)

    if (
        target.premium_until
        and target.premium_until > now
    ):
        base = target.premium_until
    else:
        base = now

    until = base + timedelta(days=days)

    await set_premium(
        target_id,
        until,
    )

    await message.answer(
        (
            "✅ Premium выдан.\n\n"
            f"👤 {target_id}\n"
            f"💎 До: {until.isoformat()}"
        )
    )


@dp.message(F.text.startswith("/createpromo"))
async def admin_create_promo(
    message: Message,
):
    if not message.from_user:
        return

    if message.from_user.id not in ADMIN_IDS:
        return

    parts = (message.text or "").split()

    if len(parts) != 4:
        await message.answer(
            (
                "Используй:\n"
                "<code>"
                "/createpromo CODE DAYS MAX_USES"
                "</code>"
            )
        )
        return

    code = parts[1].upper()

    try:
        days = int(parts[2])
        max_uses = int(parts[3])
    except ValueError:
        await message.answer(
            "❌ DAYS и MAX_USES должны быть числами."
        )
        return

    if days <= 0:
        await message.answer(
            "❌ DAYS должен быть > 0."
        )
        return

    success = await create_promo(
        code,
        days,
        max_uses,
    )

    await message.answer(
        (
            "✅ Промокод создан."
            if success
            else "❌ Такой промокод уже существует."
        )
    )


@dp.message(F.text.startswith("@"))
async def username_message(
    message: Message,
):
    user = await ensure_user(message)

    if not user:
        return

    usernames = extract_usernames(
        message.text or ""
    )

    if not usernames:
        await message.answer(
            "❌ Некорректный username."
        )
        return

    premium = await premium_active(user)

    if len(usernames) > 1:
        if not premium:
            await message.answer(
                (
                    "📦 Массовый поиск доступен "
                    "только Premium."
                )
            )
            return

        if len(usernames) > PREMIUM_BATCH_SIZE:
            await message.answer(
                (
                    f"❌ Максимум "
                    f"{PREMIUM_BATCH_SIZE} "
                    "username за раз."
                )
            )
            return

    if not premium:
        usernames = usernames[:1]

    results = []

    for username in usernames:
        allowed, reason = await can_search(
            user.id,
            username,
        )

        if not allowed:
            results.append(
                f"❌ @{username}\n{reason}"
            )
            continue

        await increment_search(
            user.id
        )

        await save_search(
            user.id,
            username,
            None,
            "telegram",
        )

        status = await telegram_check(
            username
        )

        await save_search(
            user.id,
            username,
            status,
            "telegram",
        )

        if status is True:
            text = (
                f"🟢 <b>@{username}</b>\n"
                "Предварительно свободен"
            )
        elif status is False:
            text = (
                f"🔴 <b>@{username}</b>\n"
                "Занят"
            )
        else:
            text = (
                f"🟡 <b>@{username}</b>\n"
                "Не удалось определить статус"
            )

        results.append(text)

    await message.answer(
        (
            "🔎 <b>РЕЗУЛЬТАТ ПРОВЕРКИ</b>\n\n"
            + "\n\n".join(results)
            + "\n\n"
            "⚠️ Telegram Bot API не предоставляет "
            "отдельный официальный endpoint "
            "для гарантированного определения "
            "свободного username. Поэтому "
            "«свободен» означает предварительный "
            "результат проверки."
        ),
        reply_markup=keyboard(),
    )


@dp.message()
async def fallback(
    message: Message,
):
    await ensure_user(message)

    await message.answer(
        (
            "🤔 Не понял команду.\n\n"
            "Выбери действие в меню."
        ),
        reply_markup=keyboard(),
    )


async def trap_worker():
    await asyncio.sleep(15)

    while True:
        try:
            traps = await get_active_traps()

            for trap in traps:
                try:
                    status = await telegram_check(
                        trap.username
                    )

                    previous = trap.last_status

                    await update_trap_status(
                        trap.id,
                        status,
                    )

                    if (
                        status is True
                        and previous is not True
                    ):
                        await bot.send_message(
                            trap.user_id,
                            (
                                "🚨 <b>TRAP!</b>\n\n"
                                f"🟢 @{trap.username}\n\n"
                                "Username сейчас "
                                "предварительно определяется "
                                "как свободный.\n\n"
                                "Проверь его вручную как "
                                "можно скорее."
                            ),
                        )

                except Exception:
                    logger.exception(
                        "Trap error #%s",
                        trap.id,
                    )

                await asyncio.sleep(0.3)

        except Exception:
            logger.exception(
                "Trap worker error"
            )

        await asyncio.sleep(
            TRAP_INTERVAL_SECONDS
        )


async def bot_worker():
    await init_db()

    logger.info(
        "Starting Telegram polling"
    )

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    await dp.start_polling(bot)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    bot_task = asyncio.create_task(
        bot_worker()
    )

    trap_task = asyncio.create_task(
        trap_worker()
    )

    yield

    bot_task.cancel()
    trap_task.cancel()

    await asyncio.gather(
        bot_task,
        trap_task,
        return_exceptions=True,
    )

    await bot.session.close()


app = FastAPI(
    title="TEYZUS",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "service": "TEYZUS",
        "status": "ok",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
    )
