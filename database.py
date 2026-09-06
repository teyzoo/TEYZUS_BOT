from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    select,
    func,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )
else:
    DATABASE_URL = "sqlite+aiosqlite:///./teyzus.db"


engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
    )

    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    premium_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    searches_today: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    search_date: Mapped[Optional[str]] = mapped_column(
        String(16),
        nullable=True,
    )

    referral_code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )

    referred_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    referral_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    balance: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(32),
        index=True,
    )

    available: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(32),
        default="telegram",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class Trap(Base):
    __tablename__ = "traps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(32),
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    last_status: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )

    last_checked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    code: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    premium_days: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    uses: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    max_uses: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class PromoUse(Base):
    __tablename__ = "promo_uses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    promo_id: Mapped[int] = mapped_column(
        ForeignKey("promo_codes.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )

    price: Mapped[float] = mapped_column(
        Float,
    )

    currency: Mapped[str] = mapped_column(
        String(8),
        default="RUB",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )


async def get_user(
    user_id: int,
) -> Optional[User]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()


async def create_user(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    referral_id: Optional[int] = None,
) -> User:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if user:
            user.username = username
            user.first_name = first_name

            await session.commit()
            return user

        referral_code = f"u{user_id}"

        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            referral_code=referral_code,
            referred_by=(
                referral_id
                if referral_id != user_id
                else None
            ),
        )

        session.add(user)

        if referral_id and referral_id != user_id:
            referrer_result = await session.execute(
                select(User).where(
                    User.id == referral_id
                )
            )

            referrer = (
                referrer_result.scalar_one_or_none()
            )

            if referrer:
                referrer.referral_count += 1

        await session.commit()

        return user


async def reset_daily_counter(
    user_id: int,
    today: str,
) -> User:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one()

        if user.search_date != today:
            user.search_date = today
            user.searches_today = 0

            await session.commit()

        return user


async def increment_search(
    user_id: int,
) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one()

        user.searches_today += 1

        await session.commit()


async def save_search(
    user_id: int,
    username: str,
    available: Optional[bool],
    source: str = "telegram",
) -> None:
    async with SessionLocal() as session:
        row = SearchHistory(
            user_id=user_id,
            username=username,
            available=available,
            source=source,
        )

        session.add(row)

        await session.commit()


async def add_trap(
    user_id: int,
    username: str,
) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Trap).where(
                Trap.user_id == user_id,
                Trap.username == username,
                Trap.active == True,
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            return False

        session.add(
            Trap(
                user_id=user_id,
                username=username,
                active=True,
            )
        )

        await session.commit()

        return True


async def remove_trap(
    user_id: int,
    username: str,
) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Trap).where(
                Trap.user_id == user_id,
                Trap.username == username,
                Trap.active == True,
            )
        )

        trap = result.scalar_one_or_none()

        if not trap:
            return False

        trap.active = False

        await session.commit()

        return True


async def get_active_traps():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Trap).where(
                Trap.active == True
            )
        )

        return list(result.scalars().all())


async def update_trap_status(
    trap_id: int,
    status: Optional[bool],
) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Trap).where(
                Trap.id == trap_id
            )
        )

        trap = result.scalar_one_or_none()

        if trap:
            trap.last_status = status
            trap.last_checked = utcnow()

            await session.commit()


async def set_premium(
    user_id: int,
    premium_until: Optional[datetime],
) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return False

        user.is_premium = True
        user.premium_until = premium_until

        await session.commit()

        return True


async def get_promo(
    code: str,
) -> Optional[PromoCode]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(PromoCode).where(
                PromoCode.code == code.upper()
            )
        )

        return result.scalar_one_or_none()


async def use_promo(
    user_id: int,
    promo_id: int,
) -> bool:
    async with SessionLocal() as session:
        existing = await session.execute(
            select(PromoUse).where(
                PromoUse.user_id == user_id,
                PromoUse.promo_id == promo_id,
            )
        )

        if existing.scalar_one_or_none():
            return False

        result = await session.execute(
            select(PromoCode).where(
                PromoCode.id == promo_id
            )
        )

        promo = result.scalar_one_or_none()

        if not promo or not promo.active:
            return False

        if (
            promo.max_uses > 0
            and promo.uses >= promo.max_uses
        ):
            return False

        user_result = await session.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if not user:
            return False

        now = utcnow()

        if (
            user.premium_until
            and user.premium_until > now
        ):
            base = user.premium_until
        else:
            base = now

        from datetime import timedelta

        user.is_premium = True
        user.premium_until = (
            base
            + timedelta(days=promo.premium_days)
        )

        promo.uses += 1

        session.add(
            PromoUse(
                user_id=user_id,
                promo_id=promo_id,
            )
        )

        await session.commit()

        return True


async def create_promo(
    code: str,
    premium_days: int,
    max_uses: int,
) -> bool:
    async with SessionLocal() as session:
        existing = await session.execute(
            select(PromoCode).where(
                PromoCode.code == code.upper()
            )
        )

        if existing.scalar_one_or_none():
            return False

        session.add(
            PromoCode(
                code=code.upper(),
                premium_days=premium_days,
                max_uses=max_uses,
            )
        )

        await session.commit()

        return True


async def create_listing(
    seller_id: int,
    username: str,
    price: float,
    currency: str,
    description: Optional[str],
) -> bool:
    async with SessionLocal() as session:
        existing = await session.execute(
            select(Listing).where(
                Listing.username == username,
                Listing.active == True,
            )
        )

        if existing.scalar_one_or_none():
            return False

        session.add(
            Listing(
                seller_id=seller_id,
                username=username,
                price=price,
                currency=currency,
                description=description,
            )
        )

        await session.commit()

        return True


async def get_listings(
    limit: int = 20,
):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Listing)
            .where(Listing.active == True)
            .order_by(Listing.created_at.desc())
            .limit(limit)
        )

        return list(result.scalars().all())


async def get_user_stats(
    user_id: int,
):
    async with SessionLocal() as session:
        searches = await session.execute(
            select(
                func.count(SearchHistory.id)
            ).where(
                SearchHistory.user_id == user_id
            )
        )

        traps = await session.execute(
            select(
                func.count(Trap.id)
            ).where(
                Trap.user_id == user_id,
                Trap.active == True,
            )
        )

        return (
            searches.scalar() or 0,
            traps.scalar() or 0,
        )
