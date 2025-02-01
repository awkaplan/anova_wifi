from unittest.mock import patch

import aiohttp
import pytest

from anova_wifi import AnovaApi
from anova_wifi.web_socket_containers import APCWifiDevice
from anova_wifi.websocket_handler import AnovaWebsocketHandler


@pytest.mark.asyncio
async def test_can_create() -> None:
    async with aiohttp.ClientSession() as session:
        AnovaApi(session, "", "")


@pytest.mark.asyncio
async def test_get_devices():
    async with aiohttp.ClientSession() as session:
        api = AnovaApi(session, "test", "test")

        # Use patch to mock the methods instead of direct assignment
        with patch.object(api, "authenticate", return_value=True), patch.object(
            api, "create_websocket"
        ):
            api.websocket_handler = AnovaWebsocketHandler(
                firebase_jwt="test",
                jwt="test",
                session=session,
            )
            api.websocket_handler.devices = {
                "test_id": APCWifiDevice(
                    id="test_id",
                    name="Test Oven",
                    state={},
                    device_type="oven",
                )
            }

            devices = await api.get_devices()
            assert len(devices) == 1
            assert "test_id" in devices
            assert devices["test_id"].device_type == "oven"
