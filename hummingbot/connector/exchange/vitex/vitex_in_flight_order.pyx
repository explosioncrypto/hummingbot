from decimal import Decimal
from typing import (
    Any,
    Dict
)

from hummingbot.core.event.events import (
    OrderType,
    TradeType
)
from hummingbot.connector.in_flight_order_base import InFlightOrderBase
from hummingbot.connector.exchange.vitex.vitex_api import VitexAPI

s_decimal_0 = Decimal(0)

cdef class VitexInFlightOrder(InFlightOrderBase):
    def __init__(self,
                 client_order_id: str,
                 exchange_order_id: str,
                 trading_pair: str,
                 order_type: OrderType,
                 trade_type: TradeType,
                 price: Decimal,
                 amount: Decimal,
                 initial_state: str = "Unknown"):
        super().__init__(
            client_order_id,
            exchange_order_id,
            trading_pair,
            order_type,
            trade_type,
            price,
            amount,
            initial_state
        )
        self.trade_id_set = set()
        self.execute_price = s_decimal_0

    @property
    def is_done(self) -> bool:
        return self.last_state in {"Filled", "PendingCancel", "Cancelled", "PartiallyCancelled", "Failed", "Expired"}

    @property
    def is_failure(self) -> bool:
        return self.last_state in {"PendingCancel", "Cancelled", "PartiallyCancelled", "Failed", "Expired"}

    @property
    def is_cancelled(self) -> bool:
        return self.last_state in {"Cancelled"}

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> InFlightOrderBase:
        """
            Deserialize from saved data
        """
        cdef:
            VitexInFlightOrder order = VitexInFlightOrder(
                client_order_id=data["client_order_id"],
                exchange_order_id=data["exchange_order_id"],
                trading_pair=data["trading_pair"],
                order_type=getattr(OrderType, data["order_type"]),
                trade_type=getattr(TradeType, data["trade_type"]),
                price=Decimal(data["price"]),
                amount=Decimal(data["amount"]),
                initial_state=data["last_state"]
            )
        order.executed_amount_base = Decimal(data["executed_amount_base"])
        order.executed_amount_quote = Decimal(data["executed_amount_quote"])
        order.fee_asset = data["fee_asset"]
        order.fee_paid = Decimal(data["fee_paid"])
        return order
