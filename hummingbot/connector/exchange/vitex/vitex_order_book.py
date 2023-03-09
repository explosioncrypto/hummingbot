#!/usr/bin/env python
import logging
from typing import (
    Dict,
    Optional
)

from hummingbot.core.event.events import TradeType
from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI
from hummingbot.logger import HummingbotLogger
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import (
    OrderBookMessage,
    OrderBookMessageType
)
_bob_logger = None


class VitexOrderBook(OrderBook):
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global _bob_logger
        if _bob_logger is None:
            _bob_logger = logging.getLogger(__name__)
        return _bob_logger

    @classmethod
    def snapshot_message_from_exchange(cls,
                                       msg: Dict[str, any],
                                       timestamp: float,
                                       metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": msg["trading_pair"],
            "update_id": msg_ts,
            "bids": msg["bids"],
            "asks": msg["asks"]
        }
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, content, timestamp or msg_ts)

    @classmethod
    def diff_message_from_exchange(cls,
                                   msg: Dict[str, any],
                                   timestamp: float=None,
                                   metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        # TODO: ViteX Websocket API does not support incremental depth messages, use snapshot message instead
        message_type = OrderBookMessageType.SNAPSHOT

        return OrderBookMessage(message_type, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["topic"].split(".")[1]),
            "update_id": msg["timestamp"],
            "bids": msg["data"]["bids"],
            "asks": msg["data"]["asks"]
        }, timestamp=timestamp)

    @classmethod
    def trade_message_from_exchange(cls,
                                    msg: Dict[str, any],
                                    metadata: Optional[Dict]=None):
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": msg["trading_pair"],
            "trade_type": float(TradeType.SELL.value) if msg["T"] == 2 else float(TradeType.BUY.value),
            "trade_id": msg["t"],
            "update_id": msg["t"],
            "amount": msg["q"],
            "price": msg["p"]
        }
        return OrderBookMessage(OrderBookMessageType.TRADE, content, timestamp or msg_ts)

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> OrderBook:
        retval = VitexOrderBook()
        retval.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return retval