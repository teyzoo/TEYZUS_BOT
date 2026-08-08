from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


ROLE_NAMES = {
    Role.USER: "👤 Пользователь",
    Role.MODERATOR: "🛡 Модератор",
    Role.ADMIN: "👑 Администратор",
    Role.OWNER: "💎 Владелец",
}


def is_staff(role: str) -> bool:
    return role in {
        Role.MODERATOR,
        Role.ADMIN,
        Role.OWNER,
    }


def is_admin(role: str) -> bool:
    return role in {
        Role.ADMIN,
        Role.OWNER,
    }


def is_owner(role: str) -> bool:
    return role == Role.OWNER
