import logging
from typing import Optional, Dict

from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import (
    OrderBookMessage,
    OrderBookMessageType
)
from hummingbot.logger import HummingbotLogger

_bob_logger = None


class VitexOrderBook(OrderBook):
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global _bob_logger
        if _bob_logger is None:
            _bob_logger = logging.getLogger(__name__)
        return _bob_logger

    @classmethod
    def snapshot_message_from_exchange(
        cls,
        msg: Dict[str, any],
        timestamp: float,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["trading_pair"]),
            "update_id": msg["timestamp"],
            "bids": msg["bids"],
            "asks": msg["asks"]
        }
        return OrderBookMessage(
            OrderBookMessageType.SNAPSHOT,
            content,
            timestamp=timestamp
        )

    @classmethod
    def trade_message_from_exchange(
        cls,
        msg: Dict[str, any],
        data: Dict[str, any],
        timestamp: Optional[float]=None,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["data"]["s"]),
            "trade_type": VitexAPI.convert_trade_type(msg["data"]["side"]),
            "trade_id": msg["data"]["id"],
            "update_id": msg["timestamp"],
            "price": msg["data"]["p"],
            "amount": msg["data"]["a"]
        }
        return OrderBookMessage(
            OrderBookMessageType.TRADE,
            content,
            timestamp=timestamp
        )

    @classmethod
    def diff_message_from_exchange(
        cls,
        msg: Dict[str, any],
        data: Dict[str, any],
        timestamp: Optional[float]=None,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["topic"].split(".")[1]),
            "update_id": msg["timestamp"],
            "bids": msg["data"]["bids"],
            "asks": msg["data"]["asks"]
        }
        return OrderBookMessage(
            OrderBookMessageType.DIFF,
            content,
            timestamp=timestamp
        )
