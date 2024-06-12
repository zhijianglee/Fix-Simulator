import logging
import socket
import time
import threading

from jproperties import Properties

import orderProcessor
from orderProcessor import *

from builder import *

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
        self.sequence_number = 0  # Track the sequence number for outgoing messages
        self.lock = threading.Lock()  # Lock for thread-safe message sending

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
        msg_dict = None
        if has_delimiters(message):
            print('This messsage has delimeter')
            msg_dict = parse_fix_message(message)
        else:
            print('This messsage has mo delimeter')
            msg_dict = parse_fix_message_no_delimiter(message)

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
                    print('Sequence number reset due to ResetSeqNumFlag')
                return self.create_logon_response()
            elif msg_type == '0':
                return self.create_heartbeat_response()
            elif msg_type == 'D':
                return orderProcessor.handle_order(msg_dict, self.sequence_number, conn)
            # else:
            #     return self.create_unsupported_response(msg_dict)
        else:
            print('Sent unsuccessful login')
            return self.create_login_unsuccessful_response(msg_dict, "Login unsuccessful. Please check if targetCompID "
                                                                     "is correct")

    def create_logon_response(self):

        print(self.sequence_number)
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': 'A',
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
        return fix_message

    def create_heartbeat_response(self):
        self.sequence_number += 1
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '0',
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': self.sequence_number,  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
        }
        fix_message = build_fix_message(response_fields)
        return fix_message

    def create_unsupported_response(self, msg_dict):
        self.sequence_number += 1
        response_fields = {
            '8': 'FIX.4.2',
            '9': '0',
            '35': '3',  # Reject message type
            '49': self.senderCompID,  # Use configured target
            '56': self.targetCompID,  # Use configured sender
            '34': str(self.sequence_number),  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': 'Unsupported message type',  # Text

        }
        fix_message = build_fix_message(response_fields)
        return fix_message

    def create_login_unsuccessful_response(self, msg_dict, tag58_string):
        self.sequence_number += 1
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
        return fix_message

    def send_message(self, response_fields):
        with self.lock:
            if not self.conn:
                print("No client connected to send messages.")
                return

            self.sequence_number += 1
            fix_message = build_fix_message(response_fields)
            self.conn.sendall(fix_message.encode('ascii'))
            print(f"Sent: {fix_message}")


if __name__ == "__main__":
    simulator = FIXSimulator()
    simulator.start()
