import asyncio
import json
import logging
from asyncio import Future
from typing import Any

from aiohttp import ClientSession, ClientWebSocketResponse, WebSocketError

from . import WebsocketFailure
from .web_socket_containers import (
    AnovaCommand,
    APCUpdate,
    APCWifiDevice,
    OvenUpdate,
    build_a3_payload,
    build_a6_a7_payload,
    build_oven_state_body,
    build_wifi_cooker_state_body,
)

_LOGGER = logging.getLogger(__name__)


class AnovaWebsocketHandler:
    def __init__(self, firebase_jwt: str, jwt: str, session: ClientSession):
        self._firebase_jwt = firebase_jwt
        self.jwt = jwt
        self.session = session
        self.url = f"https://devices.anovaculinary.io/?token={self._firebase_jwt}&supportedAccessories=APC&platform=android"  # noqa
        self.devices: dict[str, APCWifiDevice] = {}
        self.ws: ClientWebSocketResponse | None = None
        self._message_listener: Future[None] | None = None

    async def connect(self) -> None:
        try:
            self.ws = await self.session.ws_connect(self.url)
        except WebSocketError as ex:
            raise WebsocketFailure("Failed to connect to the websocket") from ex
        self._message_listener = asyncio.ensure_future(self.message_listener())

    async def disconnect(self) -> None:
        if self.ws is not None:
            await self.ws.close()
        if self._message_listener is not None:
            self._message_listener.cancel()

    def on_message(self, message: dict[str, Any]) -> None:
        _LOGGER.debug("Found message %s", message)
        if message["command"] in (
            AnovaCommand.EVENT_APC_WIFI_LIST,
            AnovaCommand.EVENT_APO_WIFI_LIST,
        ):
            payload = message["payload"]
            for device in payload:
                if device["cookerId"] not in self.devices:
                    self.devices[device["cookerId"]] = APCWifiDevice(
                        id=device["cookerId"],
                        name=device["name"],
                        state={},
                        device_type=device.get("type", "sous_vide"),
                    )
        elif message["command"] in (
            AnovaCommand.EVENT_APC_STATE,
            AnovaCommand.EVENT_APO_STATE,
        ):
            cooker_id = message["payload"]["cookerId"]
            if cooker_id not in self.devices:
                return
            if (ul := self.devices[cooker_id].update_listener) is not None:
                device_type = message["payload"].get("type", "sous_vide")
                update: APCUpdate | OvenUpdate
                if device_type == "oven":
                    oven_state = build_oven_state_body(message["payload"]["state"])
                    update = OvenUpdate.from_state(oven_state)
                elif "job" in message["payload"]["state"]:
                    update = build_wifi_cooker_state_body(
                        message["payload"]["state"]
                    ).to_apc_update()
                elif message["payload"]["type"] == "a3":
                    update = build_a3_payload(message["payload"]["state"])
                elif message["payload"]["type"] in {"a6", "a7"}:
                    update = build_a6_a7_payload(message["payload"]["state"])
                else:
                    return
                ul(update)

    async def message_listener(self) -> None:
        if self.ws is not None:
            async for msg in self.ws:
                self.on_message(json.loads(msg.data))
