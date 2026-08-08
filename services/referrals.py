from database.models import User


def build_referral_link(
    bot_username: str,
    user: User,
) -> str:
    return (
        f"https://t.me/{bot_username}"
        f"?start=ref_{user.referral_code}"
    )


def parse_referral_parameter(
    parameter: str | None,
) -> str | None:

    if not parameter:
        return None

    if not parameter.startswith("ref_"):
        return None

    code = parameter[4:].strip()

    if not code:
        return None

    return code
