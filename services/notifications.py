from aiogram import Bot


async def send_notification(
    bot: Bot,
    telegram_id: int,
    text: str,
) -> bool:

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
        )

        return True

    except Exception:
        return False
