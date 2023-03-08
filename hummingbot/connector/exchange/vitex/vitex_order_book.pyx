#!/usr/bin/env python
import logging
from typing import (
    Dict,
    Optional
)

from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI
from hummingbot.logger import HummingbotLogger
from hummingbot.core.data_type.order_book cimport OrderBook
from hummingbot.core.data_type.order_book_message import (
    OrderBookMessage,
    OrderBookMessageType
)

bob_logger = None


cdef class VitexOrderBook(OrderBook):
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global _logger
        if bob_logger is None:
            bob_logger = logging.getLogger(__name__),
        return bob_logger

    @classmethod
    def snapshot_message_from_exchange(cls,
                                       msg: Dict[str, any],
                                       trading_pair: str,
                                       timestamp: float,
                                       metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["trading_pair"]),
            "update_id": msg_ts,
            "bids": msg["bids"],
            "asks": msg["asks"]
        }, timestamp=timestamp or msg_ts)

    @classmethod
    def diff_message_from_exchange(cls,
                                   msg: Dict[str, any],
                                   timestamp: Optional[float]=None,
                                   metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        return OrderBookMessage(OrderBookMessageType.DIFF, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["topic"].split(".")[1]),
            "update_id": msg["timestamp"],
            "bids": msg["data"]["bids"],
            "asks": msg["data"]["asks"]
        }, timestamp=timestamp or msg_ts)

    @classmethod
    def trade_message_from_exchange(cls, 
                                    msg: Dict[str, any],
                                    timestamp: Optional[float]=None,
                                    metadata: Optional[Dict]=None):
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        data = msg["data"][0]
        return OrderBookMessage(OrderBookMessageType.TRADE, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(data["s"]),
            "trade_type": VitexAPI.convert_trade_type(data["side"]),
            "trade_id": data["id"],
            "update_id": msg_ts,
            "price": data["p"],
            "amount": data["q"]
        }, timestamp or msg_ts)

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> "OrderBook":
        result = VitexOrderBook()
        result.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return result
