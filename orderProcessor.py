import oracledb


class Order:
    def __init__(self, ClOrdID, HandleInst, Symbol, Side, TransactTime, OrderQty, OrdType, Price, TimeInForce, Account,
                 ExpireTime, ClientID, OrdRejReason, ExDestination, LastMkt, ExecBroker):
        self.ExecBroker = ExecBroker
        self.ClientID = ClientID
        self.OrdRejReason = OrdRejReason
        self.LastMkt = LastMkt
        self.ExDestination = ExDestination
        self.ExpireTime = ExpireTime
        self.Account = Account
        self.TimeInForce = TimeInForce
        self.Price = Price
        self.OrdType = OrdType
        self.OrderQty = OrderQty
        self.TransactTime = TransactTime
        self.Side = Side
        self.Symbol = Symbol
        self.HandlInst = HandleInst
        self.ClOrdID = ClOrdID


def handle_order(self, msg_dict):
    order_id = msg_dict.get('11')
    handle_inst = msg_dict.get('21')
    symbol = msg_dict.get('55')
    side = msg_dict.get('54')
    transact_time = msg_dict.get('60')
    order_qty = msg_dict.get('38')
    order_type = msg_dict.get('40')
    limit_price = msg_dict.get('44')
    time_in_force = msg_dict.get('59')
    account = msg_dict.get('1')
    expire_time = msg_dict.get('126')
    client_id = msg_dict.get('109')
    ex_destination = msg_dict.get('100')
    last_mkt = msg_dict.get('30')


def send_partial_fill(order):
    return None


def send_full_fill(order):
    return None


def send_rejection(order):
    return None


def send_cancellation(order):
    return None


def send_amendment_confirmation(order):
    return None
