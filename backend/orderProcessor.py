import time


import random
import write_to_log
from quotes_getter import get_last_price, get_bid_price
from write_to_log import *
from proccessFills import send_fills
import pytz
from proccessRejection import *

import databaseconnector
from jproperties import Properties

import sequence_manager
import sequencehandler
import simulator
from builder import *
from dictionary import *

from simulator import *
from globals import global_list
from sequence_manager import SequenceManager

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

orders_creation_related_fm = []


class Order:
    def __init__(self, ClOrdID, HandleInst, Symbol, Side, TransactTime, OrderQty, OrdType, Price, TimeInForce, Account,
                 ExpireTime, ClientID, OrdRejReason, ExDestination, LastMkt, ExecBroker, ClientCompID, SenderSubID,
                 currency, id_source, OnBehalfOfCompID, orgin_ord_id, security_id, broker_order_id=None):

        self.broker_order_id = broker_order_id
        self.security_id = security_id
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
        self.last_price = 0
        self.average_price = 0


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
    remaining_qty = order_qty
    avg_price = 0

    seq_to_use = int(sequence_number)

    order = Order(order_id, handle_inst, symbol, side, transact_time, order_qty, order_type, limit_price, time_in_force,
                  account, expire_time, client_id, None, ex_destination, last_mkt, None,
                  client_comp_id, sender_sub_id, currency, id_source, on_behalf_of_comp_id, orig_cl_ord_id, security_id)

    # List of column names
    columns = [
        "ORDER_ID", "HANDLE_INST", "SYMBOL", "ID_SOURCE", "CLIENT_COMP_ID", "SECURITY_ID",
        "SIDE", "SENDING_TIME", "ON_BEHALF_OF_COMP_ID", "TRANSACT_TIME", "ORDER_QTY",
        "SENDER_SUB_ID", "CURRENCY", "ORDER_TYPE", "LIMIT_PRICE", "TIME_IN_FORCE",
        "ACCOUNT", "EXPIRE_TIME", "CLIENT_ID", "EX_DESTINATION", "LAST_MKT",
        "EXECTYPE", "EXECTRANSTYPE", "ORDSTATUS", "PRICE", "CLIENTCOMPID",
        "SENDERSUBID", "ORIGCLORDID", "CUMULATIVE_FILLED_QUANTITY",
        "REMAINING_QTY", "AVGPRICE", "LAST_PRICE"
    ]

    # Corresponding list of values
    values = [
        order_id, handle_inst, symbol, id_source, client_comp_id, security_id, side,
        sending_time, on_behalf_of_comp_id, transact_time, order_qty, sender_sub_id,
        currency, order_type, limit_price, time_in_force, account, expire_time,
        client_id, ex_destination, last_mkt, exec_type, exec_trans_type, ord_status,
        price, client_comp_id, sender_sub_id, orig_cl_ord_id,
        cumulative_filled_quantity, remaining_qty, avg_price, get_last_price(order)
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

    (seq_to_use, valid_order) = verify_order(order, seq_to_use, conn)

    order.broker_order_id=databaseconnector.getSingleResultFromDB("SELECT BROKER_ORDER_ID FROM SIMULATOR_RECORDS WHERE ORDER_ID ='" + str(order.orgin_ord_id) + "'")
    updated_seq_num = send_order_confirmation(order, seq_to_use, conn, valid_order)

    # write_to_log.output_to_file_log_debug(configs.get('enable_auto_fill').data)

    if configs.get('enable_auto_fill').data == 'true':
        updated_seq_num = send_fills(order, updated_seq_num, conn, valid_order)

    sequencehandler.save_message_log(orders_creation_related_fm)

    return updated_seq_num


def send_order_confirmation(order, sequence_number, conn, valid_order=True):
    if valid_order:
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
            "37": str(order.broker_order_id),
            "38": str(order.OrderQty),
            "39": str(OrdStatus.New.value),
            "40": str(order.OrdType),
            "43": "N",
            "44": str(order.Price),
            "48": str(order.Symbol),
            "49": configs.get('simulator_comp_id').data,
            "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            "54": str(order.Side),
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            "55": str(order.Symbol),
            "56": str(order.ClientCompID),
            "57": str(order.SenderSubID),
            "58": str(configs.get('tag58_order_accepted').data),
            "59": str(order.TimeInForce),
            "6": "0.0000",
            "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

        }
        if order.OrdType == '1':
            response_fields.pop('44')
        fix_message = build_fix_message(response_fields)
        global_list.append(fix_message)
        orders_creation_related_fm.append(fix_message)
        conn.send(fix_message.encode('ascii'))
        sequence_number += 1
        write_to_log.output_to_file_log_debug(
            'Send order confirmation fix message: ' + build_fix_message(response_fields))

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(
                int(0)) + "' WHERE ORDER_ID =" + "'" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(int(order.OrderQty)) + "' WHERE ORDER_ID ='" + str(
                order.ClOrdID) + "'")

        databaseconnector.doInsert(
            "UPDATE SIMULATOR_RECORDS SET LAST_PRICE ='" + str(get_last_price(order)) + "' WHERE ORDER_ID ='" + str(
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

    return sequence_number


def verify_order(order, sequence_number, conn):
    #  write_to_log.output_to_file_log_debug(order.OrderQty)
    write_to_log.output_to_file_log_debug('Verifying Order Price')
    order_price_lte_zero_message = str(configs.get('order_price_lte_zero_message').data)
    extreme_order_price_message = str(configs.get('extreme_order_price_message').data)
    extreme_order_price_percentage = float(str(configs.get('extreme_order_price_percentage').data))
    should_validate_price = str(configs.get('extreme_price_validation').data)


    #  write_to_log.output_to_file_log_debug(str(order.OrdType))
    valid_order = True
    last_price = get_last_price(order)
    bid_price = get_bid_price(order)

    if order.OrdType == '2':
        if should_validate_price == 'true':

            # Determine the minimum and maximum price
            maximum_price = float(last_price) * (1 + (extreme_order_price_percentage / 100))
            minimum_price = float(last_price) * (1 - (extreme_order_price_percentage / 100))
            if float(order.Price) <= 0:
                valid_order = False
                sequence_number = send_rejection_custom_message(order, sequence_number, conn,
                                                                order_price_lte_zero_message)

            elif float(order.Price) > maximum_price:
                valid_order = False
                extreme_order_price_message = 'Limit price (' + str(order.Price) + ') above acceptable (' + str(
                    maximum_price) + ') [=bid(' + str(bid_price) + ') - ' + str(
                    extreme_order_price_percentage) + ' ticks]'
                sequence_number = send_rejection_custom_message(order, sequence_number, conn,
                                                                extreme_order_price_message)

            elif float(order.Price) < minimum_price:
                valid_order = False
                extreme_order_price_message = 'Limit price (' + str(order.Price) + ') below acceptable (' + str(
                    minimum_price) + ') [=bid(' + str(bid_price) + ') - ' + str(
                    extreme_order_price_percentage) + ' ticks]'
                sequence_number = send_rejection_custom_message(order, sequence_number, conn,
                                                                extreme_order_price_message)

            write_to_log.output_to_file_log_debug(extreme_order_price_message)
            write_to_log.output_to_file_log_debug("Extreme Price Percentage: " + str(extreme_order_price_percentage))
            write_to_log.output_to_file_log_debug(
                "Current Price Percentage" + str(((abs(float(last_price) - float(order.Price))) / float(
                    last_price)) * 100))

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET LAST_PRICE ='" + str(last_price) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    return sequence_number, valid_order
