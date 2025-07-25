import random
from datetime import datetime
import pytz

import orderProcessor
import write_to_log
import os
import socket
import time
import threading

from jproperties import Properties

import databaseconnector

import proccessAmendment
import proccessCancellation
import sequence_manager

from orderProcessor import *
from write_to_log import *
from builder import *
from globals import global_list, global_seq_num, retrieve_messages
from sequencehandler import save_sequence_number, save_message_log

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

SOH = '\x01'


def get_current_utc_time():
    from datetime import datetime
    return datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]


def send_sequence_reset(conn, new_seq_no, sender_comp_id, target_comp_id):
    # Construct a Sequence Reset message (35=4)
    seq_reset_msg = {
        '8': 'FIX.4.2',
        '9': '0',
        '35': '4',
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': str(new_seq_no),
        '36': str(new_seq_no + 1),  # New sequence number
        '52': get_current_utc_time(),

    }
    # Build final message
    message = build_fix_message(seq_reset_msg)

    # Send message to client
    conn.sendall(message.encode('utf-8'))


def load_sequence_number():
    if os.path.exists('sequence_number.json'):
        with open('sequence_number.json', 'r') as file:
            return json.load(file)
    return 1


def load_message_log():
    if os.path.exists('message_log.json'):
        with open('message_log.json', 'r') as file:
            return json.load(file)
    return []


global_conn = None


class FIXSimulator:
    def __init__(self, host='0.0.0.0', port=7418):
        self.host = host
        self.port = port
        self.senderCompID = None
        self.targetCompID = None
        self.conn = None
        self.sequence_number = load_sequence_number()
        self.message_log = []
        self.lock = threading.Lock()
        self.clear_message_log_file()
        self.client_connected = False

    def clear_message_log_file(self):
        # Clear the contents of message_log.json
        with open('message_log.json', 'w') as file:
            json.dump([], file)

    def start(self):
        thread = threading.Thread(target=self.run_server)
        thread.start()
        return thread

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            write_to_log.output_to_file_log_debug(f"Listening on {self.host}:{self.port}")
            while True:  # Loop to keep listening for connections
                conn, addr = s.accept()
                with self.lock:
                    self.conn = conn
                    self.client_connected = True
                    output_to_file_log_debug("Client connected.")
                write_to_log.output_to_file_log_debug(f"Connected by {addr}")
                threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        with conn:
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    write_to_log.output_to_file_log_debug(f"Received: {message}")
                    start_time = time.time()
                    response = self.handle_message(message, conn)
                    time.sleep(1)
                    end_time = time.time()
                    processing_time = end_time - start_time
                    write_to_log.output_to_file_log_debug(f"Processing time for message: {processing_time:.3f} seconds")
                    if response:
                        write_to_log.output_to_file_log_debug(f"Sending response: {response}")
                        conn.send(response.encode('ascii'))
            except ConnectionAbortedError as e:
                write_to_log.output_to_file_log_debug(f"Connection aborted: {e}")
            except Exception as e:
                write_to_log.output_to_file_log_debug(f"Error: {e}")
            finally:
                with self.lock:
                    self.client_connected = False
                    output_to_file_log_debug("Setting client connected to false")
                    self.conn = None
                output_to_file_log_debug("Client disconnected")

    def handle_message(self, message, conn):
        output_to_file_log_debug('Checking of client is connected')
        output_to_file_log_debug(self.client_connected)
        msg_dict = parse_fix_message(message)

        msg_type = msg_dict.get('35')
        output_to_file_log_debug('Msg Type 35' + msg_type)
        self.targetCompID = msg_dict.get('49')
        self.senderCompID = configs.get('simulator_comp_id').data


        output_to_file_log_debug(msg_dict.get('56'))
        output_to_file_log_debug(configs.get('simulator_comp_id').data)

        if msg_dict.get('56') == configs.get('simulator_comp_id').data:

            output_to_file_log_debug(msg_dict.get('56'))
            output_to_file_log_debug(configs.get('simulator_comp_id').data)
            output_to_file_log_debug('Correct Target Comp ID used by client')

            if msg_type == 'A':
                reset_seq_num_flag = msg_dict.get('141')
                if reset_seq_num_flag == 'Y':
                    self.sequence_number = 1
                    global_list.clear()
                    output_to_file_log_debug('Sequence number reset due to ResetSeqNumFlag')
                return self.create_logon_response()

            elif msg_type == '0':

                return self.create_heartbeat_response()

            elif msg_type == 'D':
                updated_sequence_number = orderProcessor.handle_order(msg_dict, self.sequence_number, conn)
                self.sequence_number = updated_sequence_number
                save_sequence_number(self.sequence_number)

            elif msg_type == 'G':

                self.sequence_number = proccessAmendment.get_amendment_request(msg_dict, self.sequence_number, conn)
                save_sequence_number(self.sequence_number)

            elif msg_type == 'F':

                self.sequence_number = proccessCancellation.cancel_request(msg_dict, self.sequence_number, conn)
                save_sequence_number(self.sequence_number)

            elif msg_type == '2':
                return self.handle_resend_request(msg_dict)

            elif msg_type == '1':
                return self.respond_test_request()

            elif msg_type == '5':
                return self.create_logout_response()
            # else:
            #     return self.create_unsupported_response(msg_dict)
        else:
            output_to_file_log_debug('Sent unsuccessful login')
            return self.create_login_unsuccessful_response(msg_dict, "Login unsuccessful. Please check if targetCompID "
                                                                     "is correct")

    def create_logon_response(self):
        global_list.clear()
        self.clear_message_log_file()
        self.sequence_number = 1
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': 'A',
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            '141': 'Y',
            '43': 'Y',
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '98': '0',  # EncryptMethod
            '108': '60',  # HeartBtInt
        }
        output_to_file_log_debug('Logon message created')
        fix_message = build_fix_message(response_fields)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        global_list.append(fix_message)
        return fix_message

    def create_logout_response(self):
        global_list.clear()
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': 'A',
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '58': 'LOgging out',
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '98': '0',  # EncryptMethod
            '108': '60',  # HeartBtInt
        }
        output_to_file_log_debug('Logout created')
        fix_message = build_fix_message(response_fields)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        global_list.append(fix_message)
        return fix_message

    def create_heartbeat_response(self):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '0',
            '43': 'Y',
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
        }
        fix_message = build_fix_message(response_fields)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        global_list.append(fix_message)

        return fix_message

    def respond_test_request(self):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '0',
            '43': 'Y',
            "112": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
        }
        output_to_file_log_debug('Responding to test request')
        fix_message = build_fix_message(response_fields)
        output_to_file_log_debug(fix_message)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        global_list.append(fix_message)

        return fix_message

    def create_unsupported_response(self, msg_dict):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '43': 'Y',
            "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
            '35': '3',  # Reject message type
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': 'Unsupported message type',  # Text

        }
        fix_message = build_fix_message(response_fields)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        global_list.append(fix_message)

        return fix_message

    def create_login_unsuccessful_response(self, msg_dict, tag58_string):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',  # Placeholder, will be updated later
            '35': '3',  # Reject message type
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': tag58_string,  # Text
            '10': '000'  # Placeholder for checksum, will be updated later
        }
        fix_message = build_fix_message(response_fields)
        global_list.append(fix_message)
        self.message_log.append(fix_message)
        self.sequence_number += 1
        save_sequence_number(self.sequence_number)
        save_message_log(self.message_log)
        return fix_message

    def send_message(self, response_fields):
        with self.lock:
            if not self.client_connected:
                output_to_file_log_debug("No client connected to send messages.")
                return
            response_fields['34'] = str(self.sequence_number)
            fix_message = build_fix_message(response_fields)
            global_list.append(fix_message)
            self.message_log.append(fix_message)
            self.sequence_number += 1
            save_sequence_number(self.sequence_number)
            save_message_log(self.message_log)
            self.conn.sendall(fix_message.encode('ascii'))
            output_to_file_log_debug(f"Sent: {fix_message}")

    def send_custom_message(self, response_fields,conn):
        sequence_number = load_sequence_number()
        if not conn:
            output_to_file_log_debug("No client connected to send messages.")
            return
        else:
            output_to_file_log_debug("Attempting to send message.")
            with self.lock:

                order_id= response_fields['11']
                broker_order_id = databaseconnector.getSingleResultFromDB(
                    "SELECT BROKER_ORDER_ID FROM SIMULATOR_RECORDS WHERE ORDER_ID ='" + str(order_id) + "'")

                response_fields['49'] = configs.get('simulator_comp_id').data
                response_fields['17'] = str(random.randint(100000, 999999))
                response_fields['37'] = str(broker_order_id)
                response_fields['52'] = datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000")
                response_fields['60'] = datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000")
                response_fields['34'] = str(sequence_number)
                fix_message = build_fix_message(response_fields)
                output_to_file_log_debug(fix_message)
                global_list.append(fix_message)
                self.message_log.append(fix_message)
                sequence_number += 1
                save_sequence_number(sequence_number)
                save_message_log(self.message_log)
                conn.sendall(fix_message.encode('ascii'))
                output_to_file_log_debug(f"Sent: {fix_message}")

    def handle_resend_request(self, msg_dict):
        output_to_file_log_debug('Responding to client request to resend fix messages:')

        # Extract the sequence numbers from the Resend Request
        begin_seq_no = int(msg_dict['7'])
        end_seq_no = int(msg_dict['16'])

        start_index = begin_seq_no - 1

        if end_seq_no == 0:
            send_sequence_reset(self.conn, begin_seq_no, self.senderCompID, self.targetCompID)

        else:
            with self.lock:
                for seq_no in range(begin_seq_no, end_seq_no + 1):
                    if seq_no - 1 < len(self.message_log):
                        message = self.message_log[seq_no - 1]
                        output_to_file_log_debug(f"Resending message: {message}")
                        self.conn.sendall(message.encode('ascii'))
                    else:
                        output_to_file_log_debug(f"Message with sequence number {seq_no} not found in message_log.")

    def regular_heartbeat(self):
        output_to_file_log_debug('Checking of client is connected')
        output_to_file_log_debug(self.client_connected)

        heart_beat = int(configs.get('heartbeat').data)
        while True:
            with self.lock:
                if self.client_connected:
                    response_fields = {
                        '8': 'FIX.4.2',
                        '9': '0',
                        '35': '0',
                        '43': 'Y',
                        "122": datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
                        '49': self.senderCompID,
                        '56': self.targetCompID,
                        '34': str(self.sequence_number),
                        '52': datetime.now(pytz.utc).strftime("%Y%m%d-%H:%M:%S.000"),
                    }
                    output_to_file_log_debug('Sending Hearbeat')
                    output_to_file_log_debug(response_fields)
                    self.send_message(response_fields)

            time.sleep(heart_beat)  # Send a heartbeat every 30 seconds


if __name__ == "__main__":
    simulator = FIXSimulator()
    simulator.start()

    # Defining global list to store fix messages that are sent out
