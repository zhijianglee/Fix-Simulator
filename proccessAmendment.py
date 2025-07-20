from jproperties import Properties

import databaseconnector
import orderProcessor
import write_to_log
from builder import build_fix_message
from globals import global_list
from orderProcessor import *
from proccessFills import send_full_fill, send_partial_fills
from write_to_log import *

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

order_amendment_related_fm = []


def get_amendment_request(msg_dict, sequence_number, conn):
    new_order_id = msg_dict.get('11')
    ori_order_id = msg_dict.get('41')
    handle_inst = msg_dict.get('21')
    symbol = msg_dict.get('55')
    id_source = msg_dict.get('22')
    client_comp_id = msg_dict.get('49')
    security_id = msg_dict.get('48')
    side = msg_dict.get('54')
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
                      None, client_comp_id, sender_sub_id, currency, id_source, on_behalf_of_comp_id, ori_order_id,
                      security_id)

    new_order.broker_order_id = databaseconnector.getSingleResultFromDB(
        "SELECT BROKER_ORDER_ID FROM SIMULATOR_RECORDS WHERE ORDER_ID ='" + str(new_order.orgin_ord_id) + "'")

    seq_to_use = int(sequence_number)

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORDER_ID='" + str(new_order_id) + "' WHERE ORIGCLORDID='" + str(
            ori_order_id) + "'")


    if int(new_order_qty) == int(configs.get('amendment_auto_reject_qty').data):
        updated_seq_num= orderProcessor.send_rejection(new_order, seq_to_use, conn)

    else:
        updated_seq_num = send_amendment(new_order, new_order_qty, ori_order_id, seq_to_use, conn)
        sequencehandler.save_message_log(order_amendment_related_fm)

    return updated_seq_num


def send_amendment(order, new_quantity, ori_order_id, sequence_number, conn):
    price = 0.00

    broker_order_id = databaseconnector.getSingleResultFromDB(
        "SELECT BROKER_ORDER_ID FROM SIMULATOR_RECORDS WHERE ORDER_ID ='" + str(new_order.orgin_ord_id) + "'")

    cum_quantity = int((databaseconnector.getSingleResultFromDB(
        "SELECT CUMULATIVE_FILLED_QUANTITY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + ori_order_id + "'")))
    write_to_log.output_to_file_log_debug(cum_quantity)

    original_quantity = int((databaseconnector.getSingleResultFromDB(
        "SELECT ORDER_QTY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + ori_order_id + "'")))

    if order.OrdType == 2 or order.OrdType == 4:
        price = float((databaseconnector.getSingleResultFromDB(
            "SELECT LIMIT_PRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'")))

    last_price = float((databaseconnector.getSingleResultFromDB(
        "SELECT LAST_PRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'")))

    average_price = float((databaseconnector.getSingleResultFromDB(
        "SELECT AVGPRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'")))

    order.last_price = last_price

    order.average_price = average_price

    oirigin_remaining_qty = int(float(databaseconnector.getSingleResultFromDB(
        "SELECT REMAINING_QTY FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'")))

    origin_order_type = databaseconnector.getSingleResultFromDB(
        "SELECT ORDER_TYPE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'")

    write_to_log.output_to_file_log_debug("Original Quantity: " + str(original_quantity))
    write_to_log.output_to_file_log_debug("New Quantity: " + str(new_quantity))

    write_to_log.output_to_file_log_debug('Constructing pending replace response fields')
    if order.OrdType == '1':
        price = 0.00

    response_fields_pending_replace = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "34": str(sequence_number),
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "43": "N",
        "49": configs.get('simulator_comp_id').data,
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "128": str(order.OnBehalfOfCompID),
        "150": str(ExecType.Pending_Replace.value),
        "151": str(oirigin_remaining_qty),
        "41": str(ori_order_id),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
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
        "40": str(origin_order_type),
        "44": str(price),
        "39": str(OrdStatus.Pending_Replace.value),
        "20": str(ExecTransType.Status.value),
        "17": str(random.randint(100000, 999999)),
        "6": str(price),
        "37": str(broker_order_id),
        "14": str(cum_quantity),
        "58": str(configs.get('tag58_amendment_pending').data),
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields_pending_replace.pop('44')

    sequence_number += 1
    fix_message = build_fix_message(response_fields_pending_replace)
    write_to_log.output_to_file_log_debug('Send Pending Amendment: ' + fix_message)
    order_amendment_related_fm.append(fix_message)
    conn.send(fix_message.encode('ascii'))

    new_remaining_quantity = int(new_quantity) - cum_quantity

    if order.OrdType == '1':
        order.Price = 0.00

    response_fields_replaced = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "34": str(sequence_number),
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "43": "Y",
        "49": configs.get('simulator_comp_id').data,
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "128": str(order.OnBehalfOfCompID),
        "150": str(ExecType.Replaced.value),
        "151": str(new_remaining_quantity),
        "41": ori_order_id,
        "21": str(order.HandlInst),
        "11": str(order.ClOrdID),  # New Order ID
        "31": "0.0000",
        "32": "0",
        "1": str(order.Account),
        "15": str(order.currency),
        "55": str(order.Symbol),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
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
        "6": str(order.Price),
        "37": str(broker_order_id),
        "14": str(cum_quantity),
        "58": str(configs.get('tag58_amendment_completed').data),
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields_replaced.pop('44')

    sequence_number += 1
    fix_message = build_fix_message(response_fields_replaced)
    write_to_log.output_to_file_log_debug('Send Replaced: ' + fix_message)
    order_amendment_related_fm.append(fix_message)
    conn.send(fix_message.encode('ascii'))
    global_list.append(fix_message)

    write_to_log.output_to_file_log_debug('After Amendment: Remaining Qty :' + str(new_remaining_quantity))

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORDER_QTY='" + str(order.OrderQty) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORDER_TYPE='" + str(order.OrdType) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET LIMIT_PRICE='" + str(order.Price) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET PRICE='" + str(order.Price) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY='" + str(new_remaining_quantity) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORIGCLORDID='" + str(order.ClOrdID) + "' WHERE ORDER_ID='" + str(
            order.ClOrdID) + "'")

    order.remaining_quantity = new_remaining_quantity

    order.executed_quantity = int((databaseconnector.getSingleResultFromDB(
        "SELECT CUMULATIVE_FILLED_QUANTITY FROM SIMULATOR_RECORDS WHERE ORDER_ID='" + order.ClOrdID + "'")))

    write_to_log.output_to_file_log_debug('Remaining Quantity to Get Filled: ' + str(order.remaining_quantity))
    write_to_log.output_to_file_log_debug('Current Executed Qty: ' + str(order.executed_quantity))
    write_to_log.output_to_file_log_debug('Current Executed Qty Last Price: ' + str(last_price))

    if int(configs.get('reject_min_qty').data) <= new_remaining_quantity <= int(configs.get('reject_max_qty').data):
        write_to_log.output_to_file_log_debug('Send Rejection')
        sequence_number = orderProcessor.send_rejection(order, sequence_number, conn)
    elif (int(configs.get('fully_fill_min_qty').data) <= new_remaining_quantity <=
          int(configs.get('fully_fill_max_qty').data)):
        write_to_log.output_to_file_log_debug('Send Full Fill')
        sequence_number = send_full_fill(order, sequence_number, conn, order.remaining_quantity,
                                         float(last_price))
    elif int(configs.get('partial_fill_min_qty').data) <= new_remaining_quantity:
        write_to_log.output_to_file_log_debug('Send PF')
        sequence_number = send_partial_fills(order, sequence_number, conn, order.remaining_quantity,
                                             float(last_price))

    return sequence_number
