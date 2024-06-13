import time
from datetime import datetime
import random

import databaseconnector
from jproperties import Properties

import simulator
from builder import *
from dictionary import *

from simulator import *
from sequence_manager import SequenceManager

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


class Order:
    def __init__(self, ClOrdID, HandleInst, Symbol, Side, TransactTime, OrderQty, OrdType, Price, TimeInForce, Account,
                 ExpireTime, ClientID, OrdRejReason, ExDestination, LastMkt, ExecBroker, ClientCompID, SenderSubID,
                 currency, id_source, OnBehalfOfCompID, orgin_ord_id=None):
        self.orgin_ord_id = orgin_ord_id
        self.OnBehalfOfCompID = OnBehalfOfCompID
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
        self.remaining_quantity = 0
        self.executed_quantity = 0
        self.filled_quantity = 0


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
    exec_type = msg_dict.get('EXECTYPE')  # Assuming these keys would be added in the future
    exec_trans_type = msg_dict.get('EXECTRANSTYPE')
    ord_status = msg_dict.get('ORDSTATUS')
    price = msg_dict.get('PRICE')
    orig_cl_ord_id = order_id
    cumulative_filled_quantity = 0
    remaining_qty = 0
    avg_price = 0

    sequence_number_from_client = msg_dict.get('34')
    print('Order Creation: Sequence Number From Client:' + sequence_number_from_client)
    print('Order Creation: Sequence Number Internal: ' + str(sequence_number))

    order = Order(order_id, handle_inst, symbol, side, transact_time, order_qty, order_type, limit_price, time_in_force,
                  account, expire_time, client_id, None, ex_destination, last_mkt, None,
                  client_comp_id, sender_sub_id, currency, id_source, on_behalf_of_comp_id)

    send_order_confirmation(order, sequence_number, conn)

    # List of column names
    columns = [
        "ORDER_ID", "HANDLE_INST", "SYMBOL", "ID_SOURCE", "CLIENT_COMP_ID", "SECURITY_ID",
        "SIDE", "SENDING_TIME", "ON_BEHALF_OF_COMP_ID", "TRANSACT_TIME", "ORDER_QTY",
        "SENDER_SUB_ID", "CURRENCY", "ORDER_TYPE", "LIMIT_PRICE", "TIME_IN_FORCE",
        "ACCOUNT", "EXPIRE_TIME", "CLIENT_ID", "EX_DESTINATION", "LAST_MKT",
        "EXECTYPE", "EXECTRANSTYPE", "ORDSTATUS", "PRICE", "CLIENTCOMPID",
        "SENDERSUBID", "ORIGCLORDID", "CUMULATIVE_FILLED_QUANTITY",
        "REMAINING_QTY", "AVGPRICE"
    ]

    # Corresponding list of values
    values = [
        order_id, handle_inst, symbol, id_source, client_comp_id, security_id, side,
        sending_time, on_behalf_of_comp_id, transact_time, order_qty, sender_sub_id,
        currency, order_type, limit_price, time_in_force, account, expire_time,
        client_id, ex_destination, last_mkt, exec_type, exec_trans_type, ord_status,
        price, client_comp_id, sender_sub_id, orig_cl_ord_id,
        cumulative_filled_quantity, remaining_qty, avg_price
    ]

    # Handle None values and format the values list for SQL query
    formatted_values = [
        f"'{value}'" if value is not None else 'NULL' for value in values
    ]

    # Construct the SQL query
    insert_query = f"""
    INSERT INTO SIMULATOR_RECORDS ({', '.join(columns)})
    VALUES ({', '.join(formatted_values)})
    """

    databaseconnector.doInsert(insert_query)

    # databaseconnector.getSingleResultFromDB(
    #     "UPDATE SIMULATOR_RECORDS SET ORIGCLORDID ='" + order_id + "' WHERE ORDER_ID =" + order_id)
    #
    # databaseconnector.getSingleResultFromDB(
    #     "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(0) + "' WHERE ORDER_ID =" + order_id)
    #
    # databaseconnector.getSingleResultFromDB(
    #     "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(0) + "' WHERE ORDER_ID =" + order_id)

    print(configs.get('enable_auto_fill').data)

    if configs.get('enable_auto_fill').data == 'true':
        return send_fills(order, sequence_number, conn)


def cancel_request(msg_dict, sequence_number, conn):
    account = msg_dict.get('1')
    new_order_id = msg_dict.get('11')
    ori_order_id = msg_dict.get('41')
    client_comp_id = msg_dict.get('49')
    sender_sub_id = msg_dict.get('50')
    handle_inst = msg_dict.get('21')
    id_source = msg_dict.get('22')
    security_id = msg_dict.get('48')
    side = msg_dict.get('54')
    symbol = msg_dict.get('55')
    ex_destination = msg_dict.get('100')
    on_behalf_of_comp_id = msg_dict.get('115')

    sequence_number_from_client = msg_dict.get('34')
    print('Order Cancellation: Sequence Number From Client:' + sequence_number_from_client)
    print('Order Cancellation: Sequence Number Internal: ' + str(sequence_number))

    cancel_order = Order(new_order_id, handle_inst, symbol, side, None, None, None,
                         None, None,
                         account, None, None, None, ex_destination, None, None,
                         client_comp_id, sender_sub_id, None, id_source, on_behalf_of_comp_id, ori_order_id)

    send_cancellation(cancel_order, sequence_number, conn)


def get_amendment_request(msg_dict, sequence_number, conn):
    new_order_id = msg_dict.get('11')
    ori_order_id = msg_dict.get('41')
    handle_inst = msg_dict.get('21')
    symbol = msg_dict.get('55')
    id_source = msg_dict.get('22')
    client_comp_id = msg_dict.get('49')
    security_id = msg_dict.get('48')
    side = msg_dict.get('54')
    sending_time = msg_dict.get('52')
    on_behalf_of_comp_id = msg_dict.get('115')
    transact_time = msg_dict.get('60')
    new_order_qty = msg_dict.get('38')
    sender_sub_id = msg_dict.get('50')
    currency = msg_dict.get('15')
    new_order_type = msg_dict.get('40')
    new_limit_price = msg_dict.get('44')
    time_in_force = msg_dict.get('59')
    account = msg_dict.get('1')
    expire_time = msg_dict.get('126')
    client_id = msg_dict.get('109')
    ex_destination = msg_dict.get('100')
    last_mkt = msg_dict.get('30')

    new_order = Order(new_order_id, handle_inst, symbol, side, transact_time, new_order_qty, new_order_type,
                      new_limit_price, time_in_force, account, expire_time, client_id, None, ex_destination, last_mkt,
                      None, client_comp_id, sender_sub_id, currency, id_source, on_behalf_of_comp_id, ori_order_id)

    sequence_number_from_client = msg_dict.get('34')
    print('Order Amendment: Sequence Number From Client:' + sequence_number_from_client)
    print('Order Amendment: Sequence Number Internal: ' + str(sequence_number))

    send_amendment(new_order, new_order_qty, ori_order_id, sequence_number, conn)

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORDER_ID='" + str(new_order_id) + "' WHERE ORIGCLORDID='" + str(
            ori_order_id) + "'")


def send_order_confirmation(order, sequence_number, conn):
    response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
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
        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.New.value),
        "40": str(order.OrdType),
        "43": "Y",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_accepted').data),
        "59": str(order.TimeInForce),
        "6": "0.0000",
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }

    conn.send(build_fix_message(response_fields).encode('ascii'))


def send_partial_fills(order, sequence_number, conn):
    order_qty = float(order.OrderQty)  # Convert to float for arithmetic operations
    partial_fill_percentage = int(configs.get('partial_fill_percentage').data)  # Retrieve the percentage

    # Calculate the target filled quantity
    target_filled_quantity = (partial_fill_percentage / 100) * order_qty

    fills_frequency_in_second = int(configs.get('fills_frequency_in_second').data)
    fill_quantity_per_frequency = int(configs.get('fill_quantity_per_frequency').data)
    average_filled_price = 0
    filled_quantity = 0
    cumulative_filled_quantity = int(order.executed_quantity)
    remaining_qty = -1

    print('Target to fill qty: ')
    print(target_filled_quantity)
    while filled_quantity < target_filled_quantity:
        remaining_qty = int(order.OrderQty) - filled_quantity
        last_price = 0

        quantity_last_fill = fill_quantity_per_frequency
        filled_quantity += quantity_last_fill
        cumulative_filled_quantity += quantity_last_fill

        if order.OrdType == '2':
            average_filled_price = order.Price
        elif order.OrdType == '1':
            average_filled_price = 0
            if configs.get('market_order_use_real_price').data == 'true':
                last_price = databaseconnector.getSingleResultFromDB(
                    "SELECT LAST_DONE_PRICE  FROM COUNTER WHERE COUNTER_CODE=" + order.Symbol)
                average_filled_price = (last_price * cumulative_filled_quantity) / cumulative_filled_quantity
            else:
                last_price = 10
                average_filled_price = (last_price * cumulative_filled_quantity) / cumulative_filled_quantity

        response_fields = {
            "8": "FIX.4.2",
            "35": str(MsgType.Execution_Report.value),
            '9': '0',
            "11": str(order.ClOrdID),
            "14": str(cumulative_filled_quantity),
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
            "37": str(random.randint(100000, 999999)),
            "38": str(order.OrderQty),
            "39": str(OrdStatus.Partially_Filled.value),
            "40": str(order.OrdType),
            "43": "N",
            "44": str(order.Price),
            "48": str(order.Symbol),
            "49": configs.get('simulator_comp_id').data,
            "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "54": str(order.Side),
            "55": str(order.Symbol),
            "56": str(order.ClientCompID),
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "128": str(order.OnBehalfOfCompID),
            "57": str(order.SenderSubID),
            "58": str(configs.get('tag58_order_executed').data),
            "59": str(order.TimeInForce),
            "75": datetime.now().strftime('%Y%m%d'),
            "6": str(average_filled_price),
            "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

        }

        time.sleep(fills_frequency_in_second)

        conn.send(build_fix_message(response_fields).encode('ascii'))

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(
                cumulative_filled_quantity) + "' WHERE ORDER_ID =" + "'" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(remaining_qty) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET AVGPRICE ='" + str(average_filled_price) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET ORDSTATUS ='" + str(
                OrdStatus.Partially_Filled.value) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET EXECTYPE ='" + str(
                ExecType.Partially_Filled.value) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET EXECTRANSTYPE ='" + str(
                ExecTransType.Status.value) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")


def send_full_fill(order, sequence_number, conn):
    average_filled_price = 0

    last_price = 0
    quantity_last_fill = int(order.OrderQty)
    filled_quantity = (int(order.OrderQty) + int(order.executed_quantity))
    remaining_qty = 0

    if order.OrdType == '2':
        average_filled_price = order.Price
    elif order.OrdType == '1':
        average_filled_price = 0
        if configs.get('market_order_use_real_price').data == 'true':
            average_filled_price = databaseconnector.getSingleResultFromDB(
                "SELECT LAST_DONE_PRICE  FROM COUNTER WHERE COUNTER_CODE=" + order.Symbol)
        else:
            average_filled_price = 10

    response_fields = {
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "14": str(filled_quantity),
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
        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.Filled.value),
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
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
        "58": str(configs.get('tag58_order_executed').data),
        "59": str(order.TimeInForce),
        "75": datetime.now().strftime('%Y%m%d'),
        "6": str(average_filled_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "8": "FIX.4.2",
    }

    conn.send(build_fix_message(response_fields).encode('ascii'))
    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(filled_quantity) + "' WHERE ORDER_ID =" + "'" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(remaining_qty) + "' WHERE ORDER_ID ='" + str(order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET AVGPRICE ='" + str(average_filled_price) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")


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
        "8": "FIX.4.2",
        "9": "0",
        "35": str(MsgType.Execution_Report.value),
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

        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.Rejected.value),
        "40": str(order.OrdType),
        "43": "Y",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
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

    }
    sequence_number += 1
    conn.send(build_fix_message(response_fields).encode('ascii'))


def send_cancellation(order, sequence_number, conn):
    cumulative_quantity = (databaseconnector.getSingleResultFromDB(
        "SELECT CUMULATIVE_FILLED_QUANTITY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    remaining_qty = (databaseconnector.getSingleResultFromDB(
        "SELECT REMAINING_QTY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    order_qty = (databaseconnector.getSingleResultFromDB(
        "SELECT ORDER_QTY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    avg_price = (databaseconnector.getSingleResultFromDB(
        "SELECT AVGPRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    ord_type = (databaseconnector.getSingleResultFromDB(
        "SELECT ORDER_TYPE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    currency = (databaseconnector.getSingleResultFromDB(
        "SELECT CURRENCY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    price = (databaseconnector.getSingleResultFromDB(
        "SELECT PRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))

    pending_cancel_response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "1": str(order.Account),
        "14": str(cumulative_quantity),
        "15": currency,
        "150": str(ExecType.Pending_Cancel.value),
        "151": str(remaining_qty),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.New.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "31": "0.0000",

        "32": "0",
        "34": str(sequence_number),
        "37": str(random.randint(100000, 999999)),
        "38": str(order_qty),
        "39": str(OrdStatus.Pending_Cancel.value),
        "40": str(ord_type),
        "41": str(order.orgin_ord_id),
        "43": "Y",
        "44": str(price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_cancel_in_prog').data),
        "59": str(order.TimeInForce),
        "6": str(avg_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    conn.send(build_fix_message(pending_cancel_response_fields).encode('ascii'))

    cancelled_response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "1": str(order.Account),
        "14": str(cumulative_quantity),
        "15": currency,
        "150": str(ExecType.Canceled.value),
        "151": str(remaining_qty),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.New.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "31": "0.0000",
        "32": "0",
        "34": str(sequence_number),
        "37": str(random.randint(100000, 999999)),
        "38": str(order_qty),
        "39": str(OrdStatus.Canceled.value),
        "40": str(ord_type),
        "41": str(order.orgin_ord_id),
        "43": "Y",
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "44": str(price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_cancel_complete').data),
        "59": str(order.TimeInForce),
        "6": str(avg_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    conn.send(build_fix_message(cancelled_response_fields).encode('ascii'))

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET EXECTRANSTYPE=" + str(ExecType.Canceled.value) + ", OrdStatus=" + str(
            OrdStatus.Canceled.value) + " WHERE ORIGCLORDID='" + str(order.orgin_ord_id) + "'")


def send_amendment(order, new_quantity, ori_order_id, sequence_number, conn):
    cum_quantity = int(databaseconnector.getSingleResultFromDB(
        "SELECT CUMULATIVE_FILLED_QUANTITY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + ori_order_id + "'"))
    print(cum_quantity)

    original_quantity = int(databaseconnector.getSingleResultFromDB(
        "SELECT ORDER_QTY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + ori_order_id + "'"))

    print(original_quantity)
    remaining_quantity = 0

    print('Constructing response fields')
    response_fields_pending_replace = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "34": str(sequence_number),
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "43": "Y",
        "49": configs.get('simulator_comp_id').data,
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "!28": str(order.OnBehalfOfCompID),
        "150": str(ExecType.Pending_Replace.value),
        "151": str(remaining_quantity),
        "41": str(ori_order_id),
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "21": str(order.HandlInst),
        "11": str(order.ClOrdID),  #New Order ID
        "31": "0.0000",
        "32": "0",
        "1": str(order.Account),
        "15": str(order.currency),
        "55": str(order.Symbol),
        "22": str(order.id_source),
        "48": str(order.Symbol),
        "54": str(order.Side),
        "38": str(original_quantity),
        "40": str(order.OrdType),

        "44": str(order.Price),
        "39": str(OrdStatus.Pending_Replace.value),
        "20": str(ExecTransType.Status.value),
        "17": str(random.randint(100000, 999999)),
        "6": "0.0000",
        "37": str(random.randint(100000, 999999)),
        "14": str(cum_quantity),
        "58": str(configs.get('tag58_amendment_pending').data),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }

    sequence_number += 1
    conn.send(build_fix_message(response_fields_pending_replace).encode('ascii'))

    remaining_quantity = int(new_quantity) - cum_quantity

    response_fields_replaced = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "34": str(sequence_number),
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "43": "Y",
        "49": configs.get('simulator_comp_id').data,
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "!28": str(order.OnBehalfOfCompID),
        "150": str(ExecType.Replaced.value),
        "151": str(remaining_quantity),
        "41": ori_order_id,
        "21": str(order.HandlInst),
        "11": str(order.ClOrdID),  # New Order ID
        "31": "0.0000",
        "32": "0",
        "1": str(order.Account),
        "15": str(order.currency),
        "55": str(order.Symbol),
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "22": str(order.id_source),
        "48": str(order.Symbol),
        "54": str(order.Side),
        "38": str(new_quantity),
        "40": str(order.OrdType),
        "59": str(order.TimeInForce),
        "44": str(order.Price),
        "39": str(OrdStatus.Pending_Replace.value),
        "20": str(ExecTransType.New.value),
        "17": str(random.randint(100000, 999999)),
        "6": "0.0000",
        "37": str(random.randint(100000, 999999)),
        "14": str(cum_quantity),
        "58": str(configs.get('tag58_amendment_completed').data),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    sequence_number += 1
    conn.send(build_fix_message(response_fields_replaced).encode('ascii'))

    print('After Amendment: Remaining Qty :' + str(remaining_quantity))

    if int(configs.get('reject_min_qty').data) <= remaining_quantity <= int(configs.get('reject_max_qty').data):
        print('Send Rejection')
        send_rejection(order, sequence_number, conn)
    elif (int(configs.get('fully_fill_min_qty').data) <= remaining_quantity <=
          int(configs.get('fully_fill_max_qty').data)):
        print('Send Full Fill')
        send_full_fill(order, sequence_number, conn)
    elif int(configs.get('partial_fill_min_qty').data) <= remaining_quantity:
        print('Send PF')
        send_partial_fills(order, sequence_number, conn)
