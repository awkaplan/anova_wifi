import asyncio
import logging
from enum import Enum
from typing import Optional

import aiohttp
from aiohttp import ClientConnectorError

from .exceptions import InvalidLogin, LoginUnreachable, NoDevicesFound, WebsocketFailure
from .websocket_handler import AnovaWebsocketHandler

_LOGGER = logging.getLogger(__name__)

# Found here - https://github.com/ammarzuberi/pyanova-api/blob/master/anova/AnovaCooker.py and personally confirmed.
ANOVA_FIREBASE_KEY = "AIzaSyDQiOP2fTR9zvFcag2kSbcmG9zPh6gZhHw"


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google.com"
    FACEBOOK = "facebook.com"
    APPLE = "apple.com"


class AnovaApi:
    """A class to handle communicating with the anova api to get devices"""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        id_token: Optional[str] = None,
        callback_url: str = "http://localhost"
    ) -> None:
        """Creates an anova api class"""
        self.session = session
        self.username = username
        self.password = password
        self.auth_provider = auth_provider
        self.id_token = id_token
        self.callback_url = callback_url
        self.jwt: str | None = None
        self._firebase_jwt: str | None = None
        self.websocket_handler: AnovaWebsocketHandler | None = None

    async def authenticate(self) -> bool:
        """Auth with Firebase server"""
        if self.auth_provider == AuthProvider.EMAIL:
            firebase_req_data = {
                "email": self.username,
                "password": self.password,
                "returnSecureToken": True,
            }
            endpoint = (
                "https://www.googleapis.com/identitytoolkit/v3/relyingparty/"
                f"verifyPassword?key={ANOVA_FIREBASE_KEY}"
            )
        else:
            if not self.id_token:
                raise InvalidLogin("ID token required for social authentication")

            firebase_req_data = {
                "postBody": f"id_token={self.id_token}&providerId={self.auth_provider}",
                "requestUri": self.callback_url,
                "returnSecureToken": True,
                "returnIdpCredential": True,
            }
            endpoint = (
                "https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?"
                f"key={ANOVA_FIREBASE_KEY}"
            )

        try:
            firebase_req = await self.session.post(
                endpoint,
                json=firebase_req_data,
            )
        except ClientConnectorError as err:
            raise LoginUnreachable(
                "Failed to connect to Anova's firebase instance"
            ) from err

        firebase_id_token_json = await firebase_req.json()
        self._firebase_jwt = firebase_id_token_json.get("idToken")

        if not self._firebase_jwt:
            raise InvalidLogin("Could not log in with Firebase")

        # Now authenticate with Anova using the Firebase ID token to get the JWT
        anova_auth_req = await self.session.post(
            "https://anovaculinary.io/authenticate",
            json={},
            headers={"firebase-token": self._firebase_jwt},
        )
        jwt_json = await anova_auth_req.json()
        jwt = jwt_json.get("jwt")  # Looks like this JWT is valid for an entire year...

        if not jwt:
            raise InvalidLogin("Could not authenticate with Anova")

        # Set JWT local variable
        self.jwt = jwt

        return True

    async def create_websocket(self) -> None:
        if self._firebase_jwt is None:
            raise WebsocketFailure("Firebase jwt was none.")
        if self.jwt is None:
            raise WebsocketFailure("jwt was none.")
        self.websocket_handler = AnovaWebsocketHandler(
            firebase_jwt=self._firebase_jwt, jwt=self.jwt, session=self.session
        )
        await self.websocket_handler.connect()
        await asyncio.sleep(5)
        if not self.websocket_handler.devices:
            raise NoDevicesFound("No devices were found on the websocket.")

    async def disconnect_websocket(self) -> None:
        if self.websocket_handler is not None:
            await self.websocket_handler.disconnect()
