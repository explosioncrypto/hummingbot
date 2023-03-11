import logging
from typing import (
    Any,
    Optional,
    Dict
)

from hummingbot.connector.exchange.vitex.vitex_order_book_message import VitexOrderBookMessage
from hummingbot.core.data_type.common import TradeType
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_message import OrderBookMessage, OrderBookMessageType
from hummingbot.logger import HummingbotLogger

_logger = None


class VitexOrderBook(OrderBook):
    @classmethod
    def logger(cls) -> HummingbotLogger:
        global _logger
        if _logger is None:
            _logger = logging.getLogger(__name__)
        return _logger

    @classmethod
    def snapshot_message_from_exchange(cls,
                                       msg: Dict[str, Any],
                                       trading_pair: str,
                                       timestamp: Optional[float]=None,
                                       metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        bids = [[float(bid["price"]),
                float(bid["quantity"])] for bid in msg["bids"]]
        asks = [[float(ask["price"]),
                float(ask["quantity"])] for ask in msg["asks"]]
        content = {
            "trading_pair": trading_pair,
            "update_id": msg_ts,
            "bids": bids,
            "asks": asks
        }
        return VitexOrderBookMessage(OrderBookMessageType.SNAPSHOT, content, timestamp or msg_ts)

    @classmethod
    def trade_message_from_exchange(cls,
                                    msg: Dict[str, Any],
                                    timestamp: Optional[float]=None,
                                    metadata: Optional[Dict]=None) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        data = msg["data"][0]
        content = {
            "trading_pair": data.get("s"),
            "trade_type": float(TradeType.SELL.value) if msg["side"] == "SELL"
            else float(TradeType.BUY.value),
            "trade_id": msg["trade_id"],
            "update_id": msg["trade_time"],
            "amount": float(msg["quantity"]),
            "price": float(msg["price"])
        }
        return VitexOrderBookMessage(OrderBookMessageType.TRADE, content, timestamp or msg_ts)

    @classmethod
    def diff_message_from_exchange(cls,
                                   data: Dict[str, Any],
                                   timestamp: float = None,
                                   metadata: Optional[Dict] = None) -> OrderBookMessage:
        if metadata:
            data.update(metadata)
        msg_ts = int(timestamp * 1e-3)
        bids = [[float(bid["price"]), float(bid["quantity"])] for bid in data.get("bids", [])]
        asks = [[float(ask["price"]), float(ask["quantity"])] for ask in data.get("asks", [])]
        content = {
            "trading_pair": data["trading_pair"],
            "update_id": msg_ts,
            "bids": bids,
            "asks": asks
        }
        return VitexOrderBookMessage(OrderBookMessageType.DIFF, content, timestamp or msg_ts)

    @classmethod
    def from_snapshot(cls, msg: OrderBookMessage) -> OrderBook:
        retval = VitexOrderBook()
        retval.apply_snapshot(msg.bids, msg.asks, msg.update_id)
        return retval
