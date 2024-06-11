import time
from datetime import datetime
import random

import oracledb
from jproperties import Properties

import simulator
from builder import *
from dictionary import *

from simulator import *

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


class Order:
    def __init__(self, ClOrdID, HandleInst, Symbol, Side, TransactTime, OrderQty, OrdType, Price, TimeInForce, Account,
                 ExpireTime, ClientID, OrdRejReason, ExDestination, LastMkt, ExecBroker, ClientCompID, SenderSubID,
                 currency, id_source):
        self.currency = currency
        self.SenderSubID = SenderSubID
        self.ClientCompID = ClientCompID
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
        self.id_source = id_source


# Need to add in all your expected keys
def handle_order(msg_dict, sequence_number, conn):
    order_id = msg_dict.get('11')
    handle_inst = msg_dict.get('21')
    symbol = msg_dict.get('55')
    id_source = msg_dict.get('22')
    client_comp_id = msg_dict.get('49')
    security_id = msg_dict.get('48')
    side = msg_dict.get('54')
    sending_time = msg_dict.get('52')
    on_behalf_of_comp_id = msg_dict.get('115')
    transact_time = msg_dict.get('60')
    order_qty = msg_dict.get('38')
    time_in_force = msg_dict.get('59')
    sender_sub_id = msg_dict.get('50')
    currency = msg_dict.get('15')
    order_type = msg_dict.get('40')
    limit_price = msg_dict.get('44')
    time_in_force = msg_dict.get('59')
    account = msg_dict.get('1')
    expire_time = msg_dict.get('126')
    client_id = msg_dict.get('109')
    ex_destination = msg_dict.get('100')
    last_mkt = msg_dict.get('30')

    order = Order(order_id, handle_inst, symbol, side, transact_time, order_qty, order_type, limit_price, time_in_force,
                  account, expire_time, client_id, None, ex_destination, last_mkt, None,
                  client_comp_id, sender_sub_id, currency, id_source)

    sequence_number += 1

    send_order_confirmation(order, sequence_number, conn)
    print(configs.get('enable_auto_fill').data)

    if configs.get('enable_auto_fill').data == 'true':
        return send_fills(order, sequence_number, conn)


def send_order_confirmation(order, sequence_number, conn):
    response_fields = {
        "11": str(order.ClOrdID),
        "14": str(0),
        "15": str(order.currency),
        "150": str(ExecType.New.value),
        "151": str(order.OrderQty),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.New.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "31": "0.0000",
        "32": "0",
        "34": str(sequence_number),
        "35": str(MsgType.Execution_Report.value),
        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.New.value),
        "40": str(order.OrdType),
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_accepted').data),
        "59": str(order.TimeInForce),
        "6": "0.0000",
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "8": "FIX.4.2",
    }

    response_message = build_fix_message(response_fields)
    response_fields['9'] = str(len(response_message) - 7)  # Update body length
    response_message = build_fix_message(response_fields)
    response_fields['10'] = calculate_checksum(response_message)  # Update checksum
    conn.send(build_fix_message(response_fields).encode('ascii'))


def send_partial_fills(order, sequence_number, conn):
    order_qty = float(order.OrderQty)  # Convert to float for arithmetic operations
    partial_fill_percentage = int(configs.get('partial_fill_percentage').data)  # Retrieve the percentage

    # Calculate the target filled quantity
    target_filled_quantity = (partial_fill_percentage / 100) * order_qty

    print(target_filled_quantity)
    fills_frequency_in_second = int(configs.get('fills_frequency_in_second').data)
    fill_quantity_per_frequency = int(configs.get('fill_quantity_per_frequency').data)
    average_filled_price = 0
    filled_quantity = 0

    while filled_quantity < target_filled_quantity:
        remaining_qty = int(order.OrderQty) - filled_quantity
        last_price = 0

        quantity_last_fill = fill_quantity_per_frequency
        filled_quantity += quantity_last_fill

        if order.OrdType == '2':
            average_filled_price = order.Price
        elif order.OrdType == '1':
            average_filled_price = 20

        response_fields = {
            "11": str(order.ClOrdID),
            "14": filled_quantity,
            "15": str(order.currency),
            "150": str(ExecType.Partially_Filled.value),
            "151": str(remaining_qty),
            "17": str(random.randint(100000, 999999)),
            "20": str(ExecTransType.Status.value),
            "21": str(order.HandlInst),
            "22": str(order.id_source),
            "31": str(last_price),
            "32": str(quantity_last_fill),
            "34": str(sequence_number),
            "35": str(MsgType.Execution_Report.value),
            "37": str(random.randint(100000, 999999)),
            "38": str(order.OrderQty),
            "39": str(OrdStatus.Partially_Filled.value),
            "40": str(order.OrdType),
            "43": "Y",
            "44": str(order.Price),
            "48": str(order.Symbol),
            "49": configs.get('simulator_comp_id').data,
            "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "54": str(order.Side),
            "55": str(order.Symbol),
            "56": str(order.ClientCompID),
            "57": str(order.SenderSubID),
            "58": str(configs.get('tag58_order_accepted').data),
            "59": str(order.TimeInForce),
            "75": datetime.now().strftime('%Y%m%d'),
            "6": str(average_filled_price),
            "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "8": "FIX.4.2",
        }

        response_message = build_fix_message(response_fields)
        response_fields['9'] = str(len(response_message) - 7)  # Update body length
        response_message = build_fix_message(response_fields)
        response_fields['10'] = calculate_checksum(response_message)  # Update checksum
        time.sleep(fills_frequency_in_second)
        conn.send(build_fix_message(response_fields).encode('ascii'))


def send_full_fill(order, sequence_number, conn):
    order_qty = float(order.OrderQty)  # Convert to float for arithmetic operations
    partial_fill_percentage = int(configs.get('partial_fill_percentage').data)  # Retrieve the percentage

    fills_frequency_in_second = int(configs.get('fills_frequency_in_second').data)
    fill_quantity_per_frequency = int(configs.get('fill_quantity_per_frequency').data)
    average_filled_price = 0
    filled_quantity = 0

    while filled_quantity < order_qty:
        remaining_qty = int(order.OrderQty) - filled_quantity
        last_price = 0

        quantity_last_fill = fill_quantity_per_frequency
        filled_quantity += quantity_last_fill

        if order.OrdType == '2':
            average_filled_price = order.Price
        elif order.OrdType == '1':
            average_filled_price = 20

        response_fields = {
            "11": str(order.ClOrdID),
            "14": filled_quantity,
            "15": str(order.currency),
            "150": str(ExecType.Filled.value),
            "151": str(remaining_qty),
            "17": str(random.randint(100000, 999999)),
            "20": str(ExecTransType.Status.value),
            "21": str(order.HandlInst),
            "22": str(order.id_source),
            "31": str(last_price),
            "32": str(quantity_last_fill),
            "34": str(sequence_number),
            "35": str(MsgType.Execution_Report.value),
            "37": str(random.randint(100000, 999999)),
            "38": str(order.OrderQty),
            "39": str(OrdStatus.Filled.value),
            "40": str(order.OrdType),
            "43": "Y",
            "44": str(order.Price),
            "48": str(order.Symbol),
            "49": configs.get('simulator_comp_id').data,
            "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "54": str(order.Side),
            "55": str(order.Symbol),
            "56": str(order.ClientCompID),
            "57": str(order.SenderSubID),
            "58": str(configs.get('tag58_order_accepted').data),
            "59": str(order.TimeInForce),
            "75": datetime.now().strftime('%Y%m%d'),
            "6": str(average_filled_price),
            "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "8": "FIX.4.2",
        }

        response_message = build_fix_message(response_fields)
        response_fields['9'] = str(len(response_message) - 7)  # Update body length
        response_message = build_fix_message(response_fields)
        response_fields['10'] = calculate_checksum(response_message)  # Update checksum
        time.sleep(fills_frequency_in_second)
        conn.send(build_fix_message(response_fields).encode('ascii'))


def send_fills(order, sequence_number, conn):
    print(order.OrderQty)

    if int(configs.get('reject_min_qty').data) <= int(order.OrderQty) <= int(configs.get('reject_max_qty').data):
        print('Send Rejection')
        send_rejection(order, sequence_number, conn)
    elif (int(configs.get('fully_fill_min_qty').data) <= int(order.OrderQty) <=
          int(configs.get('fully_fill_max_qty').data)):
        print('Send Full Fill')
        send_full_fill(order, sequence_number, conn)
    elif int(configs.get('partial_fill_min_qty').data) <= int(order.OrderQty):
        print('Send PF')
        send_partial_fills(order, sequence_number, conn)


def send_rejection(order, sequence_number, conn):
    response_fields = {
        "11": str(order.ClOrdID),
        "14": str(0),
        "15": str(order.currency),
        "150": str(ExecType.Rejected.value),
        "151": str(order.OrderQty),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.Status.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "31": "0.0000",
        "32": "0",
        "34": str(sequence_number),
        "35": str(MsgType.Execution_Report.value),
        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.Rejected.value),
        "40": str(order.OrdType),
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_reject_text').data),
        "59": str(order.TimeInForce),
        "75": datetime.now().strftime('%Y%m%d'),
        "6": "0.0000",
        "103": "0",
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "8": "FIX.4.2",
    }

    response_message = build_fix_message(response_fields)
    response_fields['9'] = str(len(response_message) - 7)  # Update body length
    response_message = build_fix_message(response_fields)
    response_fields['10'] = calculate_checksum(response_message)  # Update checksum
    conn.send(build_fix_message(response_fields).encode('ascii'))


def send_cancellation(order):
    average_filled_price = 0
    filled_quantity = 0
    remaining_qty = 0
    last_price = 0
    quantity_last_fill = 1000
    return None


def send_amendment_confirmation(order):
    return None
