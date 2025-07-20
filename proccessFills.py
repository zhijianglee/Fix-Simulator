import time
from datetime import datetime

import orderProcessor
from dictionary import *
import builder
import pytz
import databaseconnector
from builder import *
from write_to_log import *
from globals import global_list
import write_to_log
from proccessRejection import send_rejection
from simulator import *
from jproperties import Properties

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

orders_creation_related_fm = []


def send_partial_fills(order, sequence_number, conn, qty_to_fill=0, old_price=0):
    write_to_log.output_to_file_log_debug('Order Quantity: ' + order.OrderQty)
    target_filled_quantity = 0
    partial_fill_percentage = 0
    cumulative_filled_quantity = 0
    remaining_qty = 0
    average_filled_price = 0
    old_price = order.last_price
    order_value = 0

    if qty_to_fill == 0:  # This order is not coming from amendment
        order_qty = float(order.OrderQty)  # Convert to float for arithmetic operations
        write_to_log.output_to_file_log_debug('Order Quantity: ' + str(order_qty))
        partial_fill_percentage = int(configs.get('partial_fill_percentage').data)  # Retrieve the percentage
        target_filled_quantity = (partial_fill_percentage / 100) * order_qty
        remaining_qty = int(order.OrderQty) - target_filled_quantity

    else:  # This order is coming from amendment
        qty_to_fill = order.remaining_quantity
        write_to_log.output_to_file_log_debug('------- Partial Fill after Amendment --------')
        partial_fill_percentage = int(configs.get('partial_fill_percentage').data)  # Retrieve the percentage
        target_filled_quantity = (partial_fill_percentage / 100) * float(qty_to_fill)
        remaining_qty = qty_to_fill - target_filled_quantity
        cumulative_filled_quantity = int(order.executed_quantity)

    fills_frequency = int(configs.get('fills_frequency_in_second').data)
    write_to_log.output_to_file_log_debug("fills_frequency_in_second: " + str(fills_frequency))
    fill_quantity_per_frequency = int(configs.get('fill_quantity_per_frequency').data)
    write_to_log.output_to_file_log_debug("Fill quantity per frequency: " + str(fill_quantity_per_frequency))

    write_to_log.output_to_file_log_debug('Target to fill qty: ' + str(target_filled_quantity))

    # Calculate initial order value

    filled_count = 0

    existing_average_price = order.average_price
    while filled_count < target_filled_quantity:
        cumulative_filled_quantity += fill_quantity_per_frequency

        # If the order is Limit order type
        if order.OrdType == '2':
            # If the order is not coming from amendment
            write_to_log.output_to_file_log_info('Partial Fill Limit Order')
            if old_price == 0:
                average_filled_price = float(order.Price)  # Just use the price coming from fix message
                last_price = float(order.Price)

            else:  # This order is coming from amendment, so need to recalculate the average filled price
                average_filled_price = (
                        existing_average_price + (float(order.Price) * float(fill_quantity_per_frequency))
                        / float(cumulative_filled_quantity))
                last_price = float(order.Price)

        elif order.OrdType == '1':
            write_to_log.output_to_file_log_info('Partial Fill Market Order')
            if configs.get('market_order_use_real_price').data == 'true':
                last_price_lower=(float(orderProcessor.get_last_price(order))*0.98)
                last_price_upper=(float(orderProcessor.get_last_price(order))*1.02)
            #    last_price = orderProcessor.get_last_price(order)
                last_price=round(float(random.uniform(last_price_lower, last_price_upper)), 3)
                write_to_log.output_to_file_log_debug('Last Price Used Now: '+ str(last_price))
                if old_price == 0:
                    average_filled_price = (float(last_price) * float(cumulative_filled_quantity)) / float(
                        cumulative_filled_quantity)

                else:
                    average_filled_price = (
                            ((float(last_price) * float(target_filled_quantity)) + (
                                    float(old_price) * float(order.executed_quantity)))
                            / float(cumulative_filled_quantity))
            else:
                last_price = round(float(random.uniform(1.000, 99.999)), 3)
                average_filled_price = float(existing_average_price + float(
                    last_price * fill_quantity_per_frequency)) / cumulative_filled_quantity
                average_filled_price = round(float(average_filled_price), 3)

        write_to_log.output_to_file_log_debug("Average Fill price as of Now: " + str(average_filled_price))
        write_to_log.output_to_file_log_debug("Cumulative fill quantity as of now: " + str(cumulative_filled_quantity))

        order.LastMkt = str(order.ExDestination)

        filled_count += fill_quantity_per_frequency

        remaining_qty = int(order.OrderQty) - int(cumulative_filled_quantity)
        response_fields = {
            "8": "FIX.4.2",
            '9': '0',
            "35": str(MsgType.Execution_Report.value),
            "11": str(order.ClOrdID),
            "29": str(LastCapacity.Agent.value),
            "1": str(order.Account),
            "14": str(int(cumulative_filled_quantity)),
            "15": str(order.currency),
            "150": str(ExecType.Partially_Filled.value),
            "151": str(int(remaining_qty)),
            "17": str(random.randint(100000, 999999)),
            "20": str(ExecTransType.Status.value),
            "21": str(order.HandlInst),
            "22": str(order.id_source),
            "30": str(order.LastMkt),
            "31": str(last_price),
            "32": str(int(fill_quantity_per_frequency)),
            "34": str(sequence_number),
            "37": str(order.broker_order_id),
            "38": str(order.OrderQty),
            "39": str(OrdStatus.Partially_Filled.value),
            "40": str(order.OrdType),
            "43": "N",
            "44": str(order.Price),
            "48": str(order.Symbol),
            "49": configs.get('simulator_comp_id').data,
            "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            "54": str(order.Side),
            "55": str(order.Symbol),
            "56": str(order.ClientCompID),
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            "128": str(order.OnBehalfOfCompID),
            "57": str(order.SenderSubID),
            "57": str(order.SenderSubID),
            "58": str(configs.get('tag58_order_executed').data),
            "59": str(order.TimeInForce),
            "75": time.strftime('%Y%m%d'),
            "6": "{:.3f}".format(average_filled_price),
            "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

        }
        if order.OrdType == '1':
            response_fields.pop('44')

        fix_message = build_fix_message(response_fields)
        write_to_log.output_to_file_log_debug('Send PF fix message: ' + fix_message)
        orders_creation_related_fm.append(fix_message)
        conn.send(fix_message.encode('ascii'))
        global_list.append(fix_message)
        sequence_number += 1
        time.sleep(fills_frequency)

    if filled_count < target_filled_quantity:
        cumulative_filled_quantity += (target_filled_quantity - filled_count)
        remaining_qty = int(order.OrderQty) - cumulative_filled_quantity
        write_to_log.output_to_file_log_debug(
            "Checking if " + str(int(order.OrderQty) - cumulative_filled_quantity) + "equals " + str(
                int(order.OrderQty) - target_filled_quantity))
        qty_to_fill = target_filled_quantity - filled_count
        last_price = orderProcessor.get_last_price(order)
        sequence_number += send_custom_fills(order, sequence_number, conn, qty_to_fill, cumulative_filled_quantity,
                                             remaining_qty, str(ExecType.Partially_Filled.value),
                                             str(OrdStatus.Partially_Filled.value), last_price, average_filled_price)

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(
            int(cumulative_filled_quantity)) + "' WHERE ORDER_ID =" + "'" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(int(remaining_qty)) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET AVGPRICE ='" + str(average_filled_price) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET LAST_PRICE ='" + str(last_price) + "' WHERE ORDER_ID ='" + str(
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


def send_custom_fills(order, sequence_number, conn, qty_to_fill, cumulative_filled_quantity, remaining_qty, fill_type,
                      order_status, last_price, curr_avg_price):
    average_filled_price = float(curr_avg_price + float(remaining_qty * last_price)) / float(cumulative_filled_quantity)

    response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "29": str(LastCapacity.Agent.value),
        "1": str(order.Account),
        "14": str(int(cumulative_filled_quantity)),
        "15": str(order.currency),
        "150": str(fill_type),
        "151": str(int(remaining_qty)),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.Status.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "30": str(order.LastMkt),
        "31": str(last_price),
        "32": str(int(qty_to_fill)),
        "34": str(sequence_number),
        "37": str(order.broker_order_id),
        "38": str(order.OrderQty),
        "39": str(order_status),
        "40": str(order.OrdType),
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "128": str(order.OnBehalfOfCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_executed').data),
        "59": str(order.TimeInForce),
        "75": datetime.now().strftime('%Y%m%d'),
        "6": "{:.3f}".format(average_filled_price),
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields.pop('44')

    fix_message = build_fix_message(response_fields)
    write_to_log.output_to_file_log_debug('Send Fill fix message: ' + fix_message)
    conn.send(fix_message.encode('ascii'))
    global_list.append(fix_message)
    sequence_number += 1


def send_full_fill(order, sequence_number, conn, target_filled_qty=0, old_price=0):

    average_filled_price = 0
    old_price = order.last_price
    filled_quantity = 0

    quantity_last_fill = 0
    if target_filled_qty == 0:
        quantity_last_fill = int(order.OrderQty)
        filled_quantity = quantity_last_fill
    else:
        target_filled_qty = order.remaining_quantity
        quantity_last_fill = target_filled_qty
        filled_quantity = quantity_last_fill + order.executed_quantity

    remaining_qty = 0

    # If this is limit order
    if order.OrdType == '2':
        average_filled_price = order.Price
        last_price = order.Price

    # If this is market order
    elif order.OrdType == '1':
        average_filled_price = 0
        ex_destination = order.ExDestination
        feed_counter_code = order.Symbol + '.' + str(ex_destination)
        if '.' in str(order.security_id):
            feed_counter_code = order.security_id
        write_to_log.output_to_file_log_info('Partial Fill Market Order')

        if configs.get('market_order_use_real_price').data == 'true':
            last_price = orderProcessor.get_last_price(order)
            order.last_price = last_price
            average_filled_price = ((order.executed_quantity * old_price) + (
                    quantity_last_fill * float(last_price))) / filled_quantity
        else:
            last_price = 10.00
            average_filled_price = last_price

    order.LastMkt = str(order.ExDestination)
    average_filled_price = round(float(average_filled_price), 3)
    response_fields = {
        "8": "FIX.4.2",
        '9': '0',
        "35": str(MsgType.Execution_Report.value),
        "11": str(order.ClOrdID),
        "1": str(order.Account),
        "14": str(filled_quantity),
        "29": str(LastCapacity.Agent.value),
        "15": str(order.currency),
        "30": str(order.LastMkt),
        "150": str(ExecType.Filled.value),
        "151": str(remaining_qty),
        "17": str(random.randint(100000, 999999)),
        "20": str(ExecTransType.Status.value),
        "21": str(order.HandlInst),
        "22": str(order.id_source),
        "31": str(last_price),
        "32": str(quantity_last_fill),
        "34": str(sequence_number),
        "37": str(order.broker_order_id),
        "38": str(order.OrderQty),
        "39": str(OrdStatus.Filled.value),
        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "40": str(order.OrdType),
        "43": "N",
        "44": str(order.Price),
        "48": str(order.Symbol),
        "49": configs.get('simulator_comp_id').data,
        "52": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
        "54": str(order.Side),
        "55": str(order.Symbol),
        "56": str(order.ClientCompID),
        "57": str(order.SenderSubID),
        "58": str(configs.get('tag58_order_executed').data),
        "59": str(order.TimeInForce),
        "75": time.strftime('%Y%m%d'),
        "6": "{:.3f}".format(average_filled_price),
        "60": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),

    }
    if order.OrdType == '1':
        response_fields.pop('44')
    fix_message = build_fix_message(response_fields)
    orders_creation_related_fm.append(fix_message)
    write_to_log.output_to_file_log_debug('Send FF fix message: ' + fix_message)
    global_list.append(fix_message)
    sequence_number += 1

    conn.send(fix_message.encode('ascii'))
    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET CUMULATIVE_FILLED_QUANTITY ='" + str(
            filled_quantity) + "' WHERE ORDER_ID =" + "'" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET REMAINING_QTY ='" + str(remaining_qty) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET AVGPRICE ='" + str(average_filled_price) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    databaseconnector.doInsert(
        "UPDATE SIMULATOR_RECORDS SET LAST_PRICE ='" + str(last_price) + "' WHERE ORDER_ID ='" + str(
            order.ClOrdID) + "'")

    return sequence_number


def send_fills(order, sequence_number, conn, valid_order=True):
    if valid_order:
        if int(configs.get('reject_min_qty').data) <= int(order.OrderQty) <= int(configs.get('reject_max_qty').data):
            write_to_log.output_to_file_log_debug('Send Rejection')
            sequence_number = send_rejection(order, sequence_number, conn)
        elif (int(configs.get('fully_fill_min_qty').data) <= int(order.OrderQty) <=
              int(configs.get('fully_fill_max_qty').data)):
            write_to_log.output_to_file_log_debug('Send Full Fill')
            sequence_number = send_full_fill(order, sequence_number, conn)
        elif int(configs.get('partial_fill_min_qty').data) <= int(order.OrderQty):
            write_to_log.output_to_file_log_debug('Send PF')
            sequence_number = send_partial_fills(order, sequence_number, conn)

    return sequence_number
