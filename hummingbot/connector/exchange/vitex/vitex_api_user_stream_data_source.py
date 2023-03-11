#!/usr/bin/env python

import asyncio
import logging
import time
from typing import Any, AsyncIterable, Dict, Optional
import ujson
import websockets
from async_timeout import timeout
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource
from hummingbot.logger import HummingbotLogger

STREAM_URL = "wss://api.vitex.net/v2/ws"


class VitexAPIUserStreamDataSource(UserStreamTrackerDataSource):
    MESSAGE_TIMEOUT = 10.0
    # PING_TIMEOUT = 10.0  # Not used

    _vitex_logger: Optional[HummingbotLogger] = None

    @classmethod
    def logger(cls) -> HummingbotLogger:
        if cls._vitex_logger is None:
            cls._vitex_logger = logging.getLogger(__name__)
        return cls._vitex_logger

    def __init__(
        self,
        vite_address: Optional[str] = None
    ):
        self._vite_address: str = vite_address
        self._last_recv_time: float = 0
        super().__init__()

    @property
    def last_recv_time(self) -> float:
        return self._last_recv_time

    async def _inner_messages(self, ws: websockets.WebSocketClientProtocol) -> AsyncIterable[Any]:
        try:
            while True:
                with timeout(self.MESSAGE_TIMEOUT):
                    msg: str = await ws.recv()
                msg_json = ujson.loads(msg)
                event = msg_json["event"]
                if event == "push":
                    self._last_recv_time = time.time()
                    yield msg_json
        except asyncio.TimeoutError:
            self.logger().warning("WebSocket message timed out.")
        except websockets.exceptions.ConnectionClosed:
            self.logger().warning("WebSocket connection closed unexpectedly.")

    async def listen_for_user_stream(self, ev_loop: asyncio.BaseEventLoop, output: asyncio.Queue):
        while True:
            try:
                topic = f"order.{self._vite_address}"
                async with websockets.connect(STREAM_URL) as ws:
                    self._last_recv_time
