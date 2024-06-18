import socket
import time

from builder import build_fix_message


# Simple test class to verify if basic stuffs are working

def calculate_checksum(message):
    checksum = sum(ord(char) for char in message) % 256
    return str(checksum).zfill(3)


def send_message(sock, message):
    try:
        sock.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending message: {e}")


def receive_message(sock):
    try:
        data = sock.recv(1024)
        return data.decode('utf-8')
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None


def create_logon_message(sender_comp_id, target_comp_id):
    fields = {
        '8': 'FIX.4.2',
        '9': '0',
        '35': 'A',
        '49': sender_comp_id,
        "141": "Y",
        '56': target_comp_id,
        '34': '1',
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        '98': '0',
        '108': '60',
        '10': '000'
    }

    return build_fix_message(fields)


def main():
    sender_comp_id = 'OMS_OCBC_01'
    target_comp_id = 'LZJSIM'
    host = '127.0.0.1'
    port = 7418

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            print(f"Connected to {host}:{port}")

            logon_message = create_logon_message(sender_comp_id, target_comp_id)
            print(f"Sending logon message: {logon_message}")
            send_message(sock, logon_message)

            response = receive_message(sock)
            if response is not None:
                print(f"Received response: {response}")
            else:
                print("Failed to receive response.")

            proposed_order_id = "OSCBD6C41908600"
            amended_order_id = "OSCBD6C41908611"

            order_creation_message = create_order_create_request(sender_comp_id, target_comp_id, proposed_order_id)
            print(f"Sending order create message: {order_creation_message}")
            send_message(sock, order_creation_message)

            creation_response = receive_message(sock)

            if creation_response is not None:
                print(f"Received response: {creation_response}")
            else:
                print("Failed to receive response.")

                # Send order amendment message
            order_amend_message = create_order_amend_request(sender_comp_id, target_comp_id, proposed_order_id,
                                                             amended_order_id)
            print(f"Sending order amendment message: {order_amend_message}")
            send_message(sock, order_amend_message)

            amend_response = receive_message(sock)
            print(f"Received amendment response: {amend_response}")

            # Send order cancel message
            order_cancel_message = create_order_cancel_request(sender_comp_id, target_comp_id, proposed_order_id,
                                                               amended_order_id)
            print(f"Sending order cancel message: {order_cancel_message}")
            send_message(sock, order_cancel_message)

            cancel_response = receive_message(sock)

            if creation_response is not None:
                print(f"Received cancel response: {cancel_response}")
            else:
                print("Failed to receive response.")

            # Main loop to keep the client connected
            while True:
                response = receive_message(sock)
                if response is not None:
                    print(f"Received response: {response}")
                else:
                    print("Failed to receive response.")

    except Exception as e:
        print(f"Error: {e}")


def create_order_create_request(sender_comp_id, target_comp_id, proposed_order_id):
    fields = {
        '8': 'FIX.4.2',
        '9': '0',
        "35": "D",
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': '2',  # Example sequence number
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        "48": "C6L",
        "1": "0059303",
        "11": proposed_order_id,
        "15": "SGD",
        "21": "1",
        "22": "8",
        "38": "12000",
        "40": "2",
        "44": "6",
        "54": "1",
        "55": "C6L",
        "59": "0",
        "60": time.strftime("%Y%m%d-%H:%M:%S.000"),
        "100": "SI",
        "583": "515828-1",
    }

    return build_fix_message(fields)


def create_order_amend_request(sender_comp_id, target_comp_id, orig_clordid, new_order_id):
    fields = {
        '8': 'FIX.4.2',
        '9': '0',
        '35': 'G',
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': '3',  # Example sequence number
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        '11': new_order_id,  # New ClOrdID for amendment
        '41': orig_clordid,  # Original ClOrdID to amend
        '38': '15000',  # New order quantity
        '40': '2',  # Order type
        '44': '5',  # New price
        '54': '1',
        '55': 'C6L',
    }

    return build_fix_message(fields)


def create_order_cancel_request(sender_comp_id, target_comp_id, orig_clordid, cancel_order_id):
    fields = {
        '8': 'FIX.4.2',
        '9': '0',
        '35': 'F',
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': '4',  # Example sequence number
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        '11': cancel_order_id,  # New ClOrdID for cancel
        '41': orig_clordid,  # Original ClOrdID to cancel
        '54': '1',
        '55': 'C6L',
    }

    return build_fix_message(fields)


if __name__ == "__main__":
    main()
