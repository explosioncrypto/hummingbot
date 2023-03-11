#!/usr/bin/env python
import logging
from typing import (
    Dict,
    Any,
    Optional,
)

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
                                       msg: Dict[str, Any],
                                       trading_pair: str,
                                       timestamp: Optional[float]=None,
                                       metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": trading_pair,
            "update_id": msg_ts,
            "bids": msg["bids"],
            "asks": msg["asks"]
        }
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT,
                                content,
                                timestamp or msg_ts)

    @classmethod
    def trade_message_from_exchange(cls,
                                    data: Dict[str, Any],
                                    timestamp: Optional[float]=None,
                                    metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            data.update(metadata)

        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": data.get("s"),
            "trade_type": data.get("side"),
            "trade_id": data.get("id"),
            "update_id": msg_ts,
            "amount": data.get("q"),
            "price": data.get("p")
        }
        return OrderBookMessage(OrderBookMessageType.TRADE,
                                content,
                                timestamp or msg_ts)

    @classmethod
    def diff_message_from_exchange(cls,
                                   data: Dict[str, Any],
                                   timestamp: float=None,
                                   metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            data.update(metadata)

        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": data["topic"],
            "update_id": msg_ts,
            "bids": data.get("bids", []),
            "asks": data.get("asks", [])
        }
        return OrderBookMessage(OrderBookMessageType.DIFF,
                                content,
                                timestamp or msg_ts)

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> OrderBook:
        result = VitexOrderBook()
        result.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return result
