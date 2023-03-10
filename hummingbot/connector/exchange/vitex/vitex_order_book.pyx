#!/usr/bin/env python
import logging
from decimal import Decimal
from typing import (
    Dict,
    Optional
)

from hummingbot.core.event.events import TradeType
from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI
from hummingbot.logger import HummingbotLogger
from hummingbot.core.data_type.order_book cimport OrderBook
from hummingbot.core.data_type.order_book_message import (
    OrderBookMessage,
    OrderBookMessageType
)

_bob_logger = None


cdef class VitexOrderBook(OrderBook):
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
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["symbol"]),
            "update_id": msg["timestamp"],
            "bids": msg["bids"],
            "asks": msg["asks"]
        }, timestamp=timestamp)

    @classmethod
    def diff_message_from_exchange(
        cls,
        msg: Dict[str, any],
        timestamp: Optional[float]=None,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        return OrderBookMessage(OrderBookMessageType.DIFF, {
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["symbol"]),
            "update_id": msg["timestamp"],
            "bids": msg["data"]["bids"],
            "asks": msg["data"]["asks"]
        }, timestamp=timestamp)

    @classmethod
    def trade_message_from_exchange(
        cls,
        msg: Dict[str, Any],
        timestamp: Optional[float]=None,
        metadata: Optional[Dict]=None
    ) -> OrderBookMessage:
        if metadata:
            msg.update(metadata)
        ts = msg['timestamp']
        return OrderBookMessage(OrderBookMessageType.TRADE, {
            'trading_pair': VitexAPI.convert_from_exchange_trading_pair(msg['symbol']),
            'trade_type': float(TradeType.SELL.value) if msg['side'] == 'SELL' else float(TradeType.BUY.value),
            'price': Decimal(str(msg['price'])),
            'update_id': ts,
            'amount': msg['size']
        }, timestamp=ts * 1e-3)

    @classmethod
    def from_snapshot(cls, snapshot: OrderBookMessage):
        raise NotImplementedError('Vitex order book needs to retain individual order data.')

    @classmethod
    def restore_from_snapshot_and_diffs(self, snapshot: OrderBookMessage, diffs: List[OrderBookMessage]):
        raise NotImplementedError('Vitex order book needs to retain individual order data.')
