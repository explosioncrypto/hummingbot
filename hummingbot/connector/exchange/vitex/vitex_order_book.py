import logging
from typing import Optional, Dict

from hummingbot.core.data_type.common import TradeType
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
        data: Dict[str, any],
        timestamp: float,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        bids = [[float(bid["price"]), float(bid["quantity"])]
                for bid in data.get(["bids"])]
        asks = [[float(ask["price"]), float(ask["quantity"])]
                for ask in data.get(["asks"])]
        # msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": msg["symbol"],
            "update_id": msg["timestamp"],
            "bids": bids,
            "asks": asks
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
        # msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": data.get(["s"]),
            "trade_type": TradeType.SELL if data["side"] == "1" else TradeType.BUY,
            "trade_id": data.get(["id"]),
            "update_id": msg["timestamp"],
            "price": data.get(["p"]),
            "amount": data.get(["a"])
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
        bids = [[float(bid["price"]), float(bid["quantity"])]
                for bid in data.get("bids", [])]
        asks = [[float(ask["price"]), float(ask["quantity"])]
                for ask in data.get("asks", [])]
        # msg_ts = int(timestamp * 1e-3)
        content = {
            "trading_pair": msg["symbol"],
            "update_id": msg["timestamp"],
            "bids": bids,
            "asks": asks
        }
        return OrderBookMessage(
            OrderBookMessageType.SNAPSHOT,
            content,
            timestamp=timestamp
        )

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> "OrderBook":
        result = VitexOrderBook()
        result.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return result
