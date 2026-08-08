import aiohttp


class TMeChecker:

    def __init__(self) -> None:
        self.timeout = aiohttp.ClientTimeout(
            total=10
        )

    async def check(
        self,
        username: str,
    ) -> bool:

        username = username.lstrip("@")

        url = f"https://t.me/{username}"

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout
            ) as session:

                async with session.get(
                    url,
                    allow_redirects=True,
                ) as response:

                    if response.status == 404:
                        return True

                    if response.status == 200:
                        return False

                    return False

        except Exception:
            return False
