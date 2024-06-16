from jproperties import Properties

import databaseconnector
from builder import build_fix_message
from orderProcessor import *

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

order_cancel_related_fm = []


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

    seq_to_use = int(sequence_number)

    cancel_order = Order(new_order_id, handle_inst, symbol, side, None, None, None,
                         None, None,
                         account, None, None, None, ex_destination, None, None,
                         client_comp_id, sender_sub_id, None, id_source, on_behalf_of_comp_id, ori_order_id,
                         security_id)

    updated_seq_num = send_cancellation(cancel_order, seq_to_use, conn)
    sequencehandler.save_message_log(order_cancel_related_fm)
    return updated_seq_num


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
        "SELECT LIMIT_PRICE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    time_in_force = (databaseconnector.getSingleResultFromDB(
        "SELECT TIME_IN_FORCE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))
    security_id = (databaseconnector.getSingleResultFromDB(
        "SELECT SECURITY_ID FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))

    handle_inst = (databaseconnector.getSingleResultFromDB(
        "SELECT HANDLE_INST FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))

    id_source = (databaseconnector.getSingleResultFromDB(
        "SELECT ID_SOURCE FROM SIMULATOR_RECORDS WHERE ORIGCLORDID='" + order.orgin_ord_id + "'"))

    if order.HandlInst is None:
        order.HandlInst = handle_inst

    if order.id_source is None:
        order.id_source = id_source

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
        "21": str(order.handle_inst),
        "22": str(order.id_source),
        "31": "0.0000",

        "32": "0",
        "34": str(sequence_number),
        "37": str(random.randint(100000, 999999)),
        "38": str(order_qty),
        "39": str(OrdStatus.Pending_Cancel.value),
        "40": str(ord_type),
        "41": str(order.orgin_ord_id),
        "43": "N",
        "44": str(price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "52": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_cancel_in_prog').data),
        "59": str(time_in_force),
        "6": str(avg_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    fix_message = build_fix_message(pending_cancel_response_fields)
    order_cancel_related_fm.append(fix_message)
    conn.send(fix_message.encode('ascii'))
    global_list.append(fix_message)
    sequence_number += 1

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
        "43": "N",
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
        "59": str(time_in_force),
        "6": str(avg_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    fix_message = build_fix_message(cancelled_response_fields)
    order_cancel_related_fm.append(fix_message)
    conn.send(fix_message.encode('ascii'))
    sequence_number += 1

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET EXECTRANSTYPE=" + str(ExecType.Canceled.value) + ", OrdStatus=" + str(
            OrdStatus.Canceled.value) + " WHERE ORIGCLORDID='" + str(order.orgin_ord_id) + "'")

    return sequence_number
