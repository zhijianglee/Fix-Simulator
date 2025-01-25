import json
import random
import time
from datetime import datetime, timedelta

import pytz
from jproperties import Properties

import databaseconnector
import write_to_log
from builder import build_fix_message
from databaseconnector import getSingleResultFromDB
from dictionary import *
from globals import global_list
from orderProcessor import Order

orders_expiry_related_fm = []

with open("exchanges.json", "r") as file:
    exchanges = json.load(file)  # Assuming it's a list of dictionaries

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

order_records_table = configs.get('simulator_records_table').data

closing_exchanges = []
# Get current time in UTC
current_time_utc = datetime.utcnow().replace(tzinfo=pytz.utc)

def get_closing_exchanges():
    closing_exchanges.clear()
    for exchange in exchanges:
        # Get exchange time zone
        exchange_tz = pytz.timezone(exchange['time_zone'])

        # Get current time in exchange's time zone
        current_time_local = current_time_utc.astimezone(exchange_tz)

        # Get exchange closing time
        closing_time_str = exchange['closing_time']
        closing_time = datetime.strptime(closing_time_str, "%H:%M").time()

        # Allow a 2-minute window after the closing time
        closing_time_with_buffer = (datetime.combine(datetime.today(), closing_time) + timedelta(minutes=2)).time()

        # Check if current time is within the closing time window
        if closing_time <= current_time_local.time() <= closing_time_with_buffer:
            closing_exchanges.append(exchange['reuters_exchange_mnemonic'])

    print(closing_exchanges)

def parse_order(json_object):
    # Map JSON keys (case-insensitive) to the class attributes
    json_object = {k.lower(): v for k, v in json_object.items()}
    order_args = {
        attr: json_object.get(attr.lower(), None)  # Use lower-cased key lookup
        for attr in Order.__init__.__code__.co_varnames[1:]  # Skip 'self'
    }
    return Order(**order_args)

def process_expiry(sequence_number,conn):
    get_closing_exchanges()

    #Get all orders that are expiring that are placed today
    query="Select * from "+order_records_table+" where exchange in ('" + "','".join(closing_exchanges) + "') WHERE SENDING_TIME >= CURRENT_DATE AND TimeInForce IN ('0','3')"

    expiring_orders=databaseconnector.get_result_from_db(query)

    for order in expiring_orders:
        order_obj = parse_order(order)
        if order_obj.TimeInForce == '0':
            # Order is Day order
            exec_type = ExecType.Expired.value
            order_status = OrdStatus.Expired.value
            sequence_number = send_expiry_notification(sequence_number,conn,order_obj,exec_type,order_status)

    return sequence_number

def send_expiry_notification(sequence_number,conn,order,exec_type,order_status):
    # Send expiry notification
    response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "1": str(order.Account),
        "14": str(order.filled_quantity),
        "29": str(LastCapacity.Agent.value),
        "15": str(order.currency),
        "30": str(order.LastMkt),
        "150": str(exec_type),
        "151": str(order.remaining_quantity),
        "17": str(random.randint(100000, 999999)),
        "20": str(0),
        "21": str(order.HandleInst),
        "22": str(order.id_source),
        "31": str(order.last_price),
        "32": str(0),
        "34": str(sequence_number),
        "37": str(random.randint(100000, 999999)),
        "38": str(order.OrderQty),
        "39": str(order_status),
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
        "58": str(configs.get('tag58_dfd_message').data),
        "59": str(order.TimeInForce),
        "75": time.strftime('%Y%m%d'),
        "6": "{:.3f}".format(order.average_price),
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields.pop('44')
    fix_message = build_fix_message(response_fields)
    orders_expiry_related_fm.append(fix_message)
    write_to_log.output_to_file_log_debug('Send DFD fix message: ' + fix_message)
    global_list.append(fix_message)
    sequence_number += 1

    conn.send(fix_message.encode('ascii'))
    return sequence_number