#!/usr/bin/env python
import logging
from decimal import Decimal
from typing import (
    Dict,
    List,
    Optional,
)
from sqlalchemy.engine import RowProxy
import ujson
from datetime import datetime
from aiokafka import ConsumerRecord

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
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["trading_pair"]),
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
            "trading_pair": VitexAPI.convert_from_exchange_trading_pair(msg["topic"].split(".")[1]),
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
        data = msg["data"][0]
        return OrderBookMessage(OrderBookMessageType.TRADE, {
            'trading_pair': VitexAPI.convert_from_exchange_trading_pair(data["s"]),
            'trade_type': float(TradeType.SELL.value) if msg['side'] == 'SELL' else float(TradeType.BUY.value),
            "trade_id": msg["uuid"],
            'update_id': ts,
            'price': Decimal(str(msg['price'])),
            'amount': msg['size']
        }, timestamp=ts * 1e-3)

    @classmethod
    def snapshot_message_from_db(cls, record: RowProxy, metadata: Optional[Dict] = None) -> OrderBookMessage:
        msg = record.json if type(record.json) == dict else ujson.loads(record.json)
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, msg, timestamp=record.timestamp * 1e-3)

    @classmethod
    def diff_message_from_db(cls, record: RowProxy, metadata: Optional[Dict] = None) -> OrderBookMessage:
        return OrderBookMessage(OrderBookMessageType.DIFF, record.json)

    @classmethod
    def snapshot_message_from_kafka(cls, record: ConsumerRecord, metadata: Optional[Dict] = None) -> OrderBookMessage:
        msg = ujson.loads(record.value.decode())
        return OrderBookMessage(OrderBookMessageType.SNAPSHOT, msg, timestamp=record.timestamp * 1e-3)

    @classmethod
    def diff_message_from_kafka(cls, record: ConsumerRecord, metadata: Optional[Dict] = None) -> OrderBookMessage:
        msg = ujson.loads(record.value.decode())
        return OrderBookMessage(OrderBookMessageType.DIFF, msg)

    @classmethod
    def trade_receive_message_from_db(cls, record: RowProxy, metadata: Optional[Dict] = None):
        return OrderBookMessage(OrderBookMessageType.TRADE, record.json)
    @classmethod
    def from_snapshot(cls, snapshot: OrderBookMessage):
        raise NotImplementedError('Vitex order book needs to retain individual order data.')

    @classmethod
    def restore_from_snapshot_and_diffs(self, snapshot: OrderBookMessage, diffs: List[OrderBookMessage]):
        raise NotImplementedError('Vitex order book needs to retain individual order data.')
