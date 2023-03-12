import logging
from typing import Any, Optional, Dict

from hummingbot.connector.exchange.vitex.vitex_order_book_message import VitexOrderBookMessage
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import OrderBookMessage, OrderBookMessageType
from hummingbot.logger import HummingbotLogger
from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI

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
        msg: Dict[str, Any],
        trading_pair: str,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["trading_pair"]),
            "update_id": msg["timestamp"],
            "bids": msg["bids"],
            "asks": msg["asks"]
        }
        return VitexOrderBookMessage(
            OrderBookMessageType.SNAPSHOT,
            content,
            timestamp=timestamp or msg_ts
        )

    @classmethod
    def trade_message_from_exchange(
        cls,
        msg: Dict[str, Any],
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        data = msg["data"][0]
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(data["s"]),
            "trade_type": VitexAPI.convert_trade_type(data["side"]),
            "trade_id": data["id"],
            "update_id": msg_ts,
            "price": data["p"],
            "amount": data["q"]
        }
        return VitexOrderBookMessage(
            OrderBookMessageType.TRADE,
            content,
            timestamp=timestamp or msg_ts
        )

    @classmethod
    def diff_message_from_exchange(
        cls,
        msg: Dict[str, Any],
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(
                msg["topic"].split(".")[1]),
            "update_id": msg["timestamp"],
            "bids": msg["data"]["bids"],
            "asks": msg["data"]["asks"]
        }
        return VitexOrderBookMessage(
            OrderBookMessageType.SNAPSHOT,
            content,
            timestamp=timestamp or msg_ts
        )

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> OrderBook:
        result = VitexOrderBook()
        result.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return result
