import secrets
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


def generate_referral_code() -> str:
    return secrets.token_urlsafe(8)


async def get_user(
    session: AsyncSession,
    telegram_id: int,
) -> Optional[User]:
    result = await session.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    language: str,
    referred_by: Optional[int] = None,
) -> User:

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language=language or "ru",
        referred_by=referred_by,
        referral_code=generate_referral_code(),
    )

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    language: str,
    referred_by: Optional[int] = None,
) -> tuple[User, bool]:

    user = await get_user(
        session=session,
        telegram_id=telegram_id,
    )

    if user:
        changed = False

        if user.username != username:
            user.username = username
            changed = True

        if user.first_name != first_name:
            user.first_name = first_name
            changed = True

        if user.last_name != last_name:
            user.last_name = last_name
            changed = True

        if user.language != language:
            user.language = language or "ru"
            changed = True

        if changed:
            await session.commit()
            await session.refresh(user)

        return user, False

    user = await create_user(
        session=session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language=language,
        referred_by=referred_by,
    )

    return user, True
