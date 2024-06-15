import logging
import socket
import time
import threading

from jproperties import Properties

import databaseconnector
import orderProcessor
import proccessAmendment
import proccessCancellation
import sequence_manager

from orderProcessor import *

from builder import *
from globals import global_list, global_seq_num
from sequence_manager import SequenceManager

sequence_manager = None

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

SOH = '\x01'


class FIXSimulator:
    def __init__(self, host='0.0.0.0', port=7418):
        self.host = host
        self.port = port
        self.senderCompID = None
        self.targetCompID = None
        self.conn = None
        self.sequence_number = 1
        self.lock = threading.Lock()

    def start(self):
        thread = threading.Thread(target=self.run_server)
        thread.start()
        return thread

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            while True:  # Loop to keep listening for connections
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                self.conn = conn
                threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        with conn:
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received: {message}")
                    start_time = time.time()
                    response = self.handle_message(message, conn)
                    time.sleep(1)
                    end_time = time.time()
                    processing_time = end_time - start_time
                    print(f"Processing time for message: {processing_time:.3f} seconds")
                    if response:
                        print(f"Sending response: {response}")
                        conn.send(response.encode('ascii'))
            except ConnectionAbortedError as e:
                print(f"Connection aborted: {e}")
            except Exception as e:
                print(f"Error: {e}")

    def handle_message(self, message, conn):

        msg_dict = parse_fix_message(message)

        msg_type = msg_dict.get('35')
        print('Msg Type 35' + msg_type)
        self.targetCompID = msg_dict.get('49')
        self.senderCompID = configs.get('simulator_comp_id').data
        #    self.senderCompID = msg_dict.get('56')
        print(msg_dict.get('56'))
        print(configs.get('simulator_comp_id').data)

        if msg_dict.get('56') == configs.get('simulator_comp_id').data:

            print(msg_dict.get('56'))
            print(configs.get('simulator_comp_id').data)
            print('Correct Target Comp ID used by client')

            if msg_type == 'A':
                reset_seq_num_flag = msg_dict.get('141')
                if reset_seq_num_flag == 'Y':
                    self.sequence_number = 1
                    global_list.clear()
                    print('Sequence number reset due to ResetSeqNumFlag')
                return self.create_logon_response()

            elif msg_type == '0':

                return self.create_heartbeat_response()

            elif msg_type == 'D':
                updated_sequence_number = orderProcessor.handle_order(msg_dict, self.sequence_number, conn)
                self.sequence_number = updated_sequence_number

            elif msg_type == 'G':

                self.sequence_number = proccessAmendment.get_amendment_request(msg_dict, self.sequence_number, conn)

            elif msg_type == 'F':

                self.sequence_number = proccessCancellation.cancel_request(msg_dict, self.sequence_number, conn)

            elif msg_type == '2':
                return self.handle_resend_request(msg_dict)

            elif msg_type == '1':
                return self.respond_test_request()

            elif msg_type == '5':
                return self.create_logout_response()
            # else:
            #     return self.create_unsupported_response(msg_dict)
        else:
            print('Sent unsuccessful login')
            return self.create_login_unsuccessful_response(msg_dict, "Login unsuccessful. Please check if targetCompID "
                                                                     "is correct")

    def create_logon_response(self):
        global_list.clear()
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': 'A',
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            '141': 'Y',
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '98': '0',  # EncryptMethod
            '108': '60',  # HeartBtInt
        }
        print('Logon message created')
        fix_message = build_fix_message(response_fields)
        self.sequence_number += 1
        global_list.append(fix_message)
        return fix_message

    def create_logout_response(self):
        global_list.clear()
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': 'A',
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '58': 'LOgging out',
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '98': '0',  # EncryptMethod
            '108': '60',  # HeartBtInt
        }
        print('Logout created')
        fix_message = build_fix_message(response_fields)
        self.sequence_number += 1
        global_list.append(fix_message)
        return fix_message

    def create_heartbeat_response(self):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '0',
            '43': 'Y',
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
        }
        fix_message = build_fix_message(response_fields)
        self.sequence_number += 1
        global_list.append(fix_message)

        return fix_message

    def respond_test_request(self):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '0',
            '43': 'Y',
            "112": time.strftime("%Y%m%d-%H:%M:%S.000"),
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
        }
        print('Responding to test request')
        fix_message = build_fix_message(response_fields)
        print(fix_message)
        self.sequence_number += 1
        global_list.append(fix_message)

        return fix_message

    def create_unsupported_response(self, msg_dict):

        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '43': 'Y',
            "122": time.strftime("%Y%m%d-%H:%M:%S.000"),
            '35': '3',  # Reject message type
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': 'Unsupported message type',  # Text

        }
        fix_message = build_fix_message(response_fields)
        self.sequence_number = +1
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
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': tag58_string,  # Text
            '10': '000'  # Placeholder for checksum, will be updated later
        }
        fix_message = build_fix_message(response_fields)
        global_list.append(fix_message)
        self.sequence_number = +1
        return fix_message

    def send_message(self, response_fields):

        with self.lock:
            if not self.conn:
                print("No client connected to send messages.")
                return

            response_fields['34'] = str(self.sequence_number)
            fix_message = build_fix_message(response_fields)
            global_list.append(fix_message)
            self.sequence_number += 1
            self.conn.sendall(fix_message.encode('ascii'))
            print(f"Sent: {fix_message}")

    def handle_resend_request(self, msg_dict):
        print('Responding to client request to resend fix messages:')

        from_seq = msg_dict.get('7')
        to_seq = msg_dict.get('16')
        print('Size of global list: ')
        print(global_list.__len__())

        start_index = (int(from_seq) - 1)
        end_index = 0
        if to_seq == '0':
            end_index = global_list.__len__()

        else:
            end_index = int(to_seq)

        while start_index < end_index:
            fix_message = global_list[start_index]
            self.conn.sendall(fix_message.encode('ascii'))
            print("Fix Message Sent: " + fix_message)
            start_index += 1


if __name__ == "__main__":
    simulator = FIXSimulator()
    simulator.start()

    # Defining global list to store fix messages that are sent out
