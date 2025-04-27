
import random
import time
from datetime import datetime

import pytz

import databaseconnector

from jproperties import Properties
from write_to_log import *
import write_to_log
import sequencehandler
from builder import build_fix_message
from dictionary import *
from globals import global_list
#from sequencehandler import orders_creation_related_fm

from write_to_log import output_to_file_log_debug
orders_rejection_related_fm = []

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


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
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "49": configs.get('simulator_comp_id').data,
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_reject_text').data),
        "59": str(order.TimeInForce),
        "75": time.strftime('%Y%m%d'),
        "6": "0.0000",
        "103": "0",
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields.pop('44')

    sequence_number += 1
    fix_message = build_fix_message(response_fields)
    output_to_file_log_debug('Send Reject message: ' + fix_message)
    conn.send(fix_message.encode('ascii'))
    global_list.append(fix_message)
    orders_rejection_related_fm.append(fix_message)
    sequencehandler.save_message_log(orders_rejection_related_fm)
    return sequence_number


def send_rejection_custom_message(order, sequence_number, conn, message):
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
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "49": configs.get('simulator_comp_id').data,
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(message),
        "59": str(order.TimeInForce),
        "75": time.strftime('%Y%m%d'),
        "6": "0.0000",
        "103": "0",
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields.pop('44')

    sequence_number += 1
    fix_message = build_fix_message(response_fields)
    output_to_file_log_debug('Send Reject message: ' + fix_message)
    conn.send(fix_message.encode('ascii'))
    global_list.append(fix_message)
    orders_rejection_related_fm.append(fix_message)
    sequencehandler.save_message_log(orders_rejection_related_fm)
    return sequence_number
