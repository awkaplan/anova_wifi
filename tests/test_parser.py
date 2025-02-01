import aiohttp
import pytest

from anova_wifi import AnovaApi


@pytest.mark.asyncio
async def test_can_create() -> None:
    async with aiohttp.ClientSession() as session:
        AnovaApi(session, "", "")
