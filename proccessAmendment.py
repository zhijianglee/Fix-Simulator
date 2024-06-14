from jproperties import Properties

import databaseconnector
import orderProcessor
from builder import build_fix_message
from globals import global_list
from orderProcessor import *

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


def get_amendment_request(msg_dict, sequence_number, conn):
    new_order_id = msg_dict.get('11')
    ori_order_id = msg_dict.get('41')
    handle_inst = msg_dict.get('21')
    symbol = msg_dict.get('55')
    id_source = msg_dict.get('22')
    client_comp_id = msg_dict.get('49')
    security_id = msg_dict.get('48')
    side = msg_dict.get('54')
    msg_seq_num = msg_dict.get('34')
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

    seq_to_use = int(sequence_number)

    updated_seq_num = send_amendment(new_order, new_order_qty, ori_order_id, seq_to_use, conn)

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET ORDER_ID='" + str(new_order_id) + "' WHERE ORIGCLORDID='" + str(
            ori_order_id) + "'")
    return updated_seq_num


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
        "43": "N",
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
    global_list.append(build_fix_message(response_fields_replaced))

    print('After Amendment: Remaining Qty :' + str(remaining_quantity))

    if int(configs.get('reject_min_qty').data) <= remaining_quantity <= int(configs.get('reject_max_qty').data):
        print('Send Rejection')
        orderProcessor.send_rejection(order, sequence_number, conn)
    elif (int(configs.get('fully_fill_min_qty').data) <= remaining_quantity <=
          int(configs.get('fully_fill_max_qty').data)):
        print('Send Full Fill')
        orderProcessor.send_full_fill(order, sequence_number, conn)
    elif int(configs.get('partial_fill_min_qty').data) <= remaining_quantity:
        print('Send PF')
        orderProcessor.send_partial_fills(order, sequence_number, conn)

    return sequence_number
