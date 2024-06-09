import socket
import time
import threading

from builder import *


class FIXSimulator:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.senderCompID = None
        self.targetCompID = None
        self.conn = None
        self.sequence_number = 1  # Track the sequence number for outgoing messages
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
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(f"Received: {message}")
                response = self.handle_message(message)
                conn.sendall(response.encode('utf-8'))

    def handle_message(self, message):
        msg_dict = parse_fix_message(message)
        msg_type = msg_dict.get('35')
        self.targetCompID = msg_dict.get('49')
        self.senderCompID = msg_dict.get('56')
        match msg_type:
            case 'A':
                return self.create_logon_response(msg_dict)
            case '0':
                return self.create_heartbeat_response(msg_dict)
            case _:
                return self.create_unsupported_response(msg_dict)

    def create_logon_response(self, msg_dict):
        response_fields = {
            '8': 'FIX.4.2',
            '9': '000',  # Placeholder, will be updated later
            '35': 'A',
            '49': self.targetCompID,  # Use configured target
            '56': self.senderCompID,  # Use configured sender
            '34': '1',  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '98': '0',  # EncryptMethod
            '108': '30',  # HeartBtInt
            '10': '000'  # Placeholder for checksum, will be updated later
        }
        print('Logon message created')
        response_message = build_fix_message(response_fields)
        response_fields['9'] = str(len(response_message) - 7)  # Update body length
        response_message = build_fix_message(response_fields)
        response_fields['10'] = calculate_checksum(response_message)  # Update checksum
        print('Logon message sent')
        return build_fix_message(response_fields)

    def create_heartbeat_response(self, msg_dict):
        response_fields = {
            '8': 'FIX.4.2',
            '9': '000',  # Placeholder, will be updated later
            '35': '0',
            '49': self.targetCompID,  # Use configured target
            '56': self.senderCompID,  # Use configured sender
            '34': '2',  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '10': '000'  # Placeholder for checksum, will be updated later
        }
        response_message = build_fix_message(response_fields)
        response_fields['9'] = str(len(response_message) - 7)  # Update body length
        response_message = build_fix_message(response_fields)
        response_fields['10'] = calculate_checksum(response_message)  # Update checksum
        return build_fix_message(response_fields)

    def create_unsupported_response(self, msg_dict):
        response_fields = {
            '8': 'FIX.4.2',
            '9': '000',  # Placeholder, will be updated later
            '35': '3',  # Reject message type
            '49': self.targetCompID,  # Use configured target
            '56': self.senderCompID,  # Use configured sender
            '34': '3',  # Message sequence number
            '52': time.strftime("%Y%m%d-%H:%M:%S.000"),  # Sending time
            '45': msg_dict['34'],  # Reference sequence number
            '58': 'Unsupported message type',  # Text
            '10': '000'  # Placeholder for checksum, will be updated later
        }
        response_message = build_fix_message(response_fields)
        response_fields['9'] = str(len(response_message) - 7)  # Update body length
        response_message = build_fix_message(response_fields)
        response_fields['10'] = calculate_checksum(response_message)  # Update checksum
        return build_fix_message(response_fields)

    def send_message(self, response_message):
        with self.lock:
            if not self.conn:
                print("No client connected to send messages.")
                return

            self.sequence_number += 1
            self.conn.sendall(response_message.encode('utf-8'))
            print(f"Sent: {response_message}")


if __name__ == "__main__":
    simulator = FIXSimulator()
    simulator.start()
