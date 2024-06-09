import socket
import time


def calculate_checksum(message):
    checksum = sum(ord(char) for char in message) % 256
    return str(checksum).zfill(3)


def build_fix_message(fields):
    return ''.join([f"{key}={value}\x01" for key, value in fields.items()])


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
        '35': 'A',
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': '1',
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        '98': '0',
        '108': '30',
        '10': '000'
    }
    message = build_fix_message(fields)
    fields['9'] = str(len(message) - 7)
    message = build_fix_message(fields)
    fields['10'] = calculate_checksum(message)
    return build_fix_message(fields)


def main():
    sender_comp_id = 'OMS_OCBC_01'
    target_comp_id = 'SIM_LZJ_01'
    host = '127.0.0.1'
    port = 5000

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

            # Main loop to keep the client connected
            while True:
                response = receive_message(sock)
                if response is not None:
                    print(f"Received response: {response}")
                else:
                    print("Failed to receive response.")
    except Exception as e:
        print(f"Error: {e}")


def create_custom_message(msg_type, sender_comp_id, target_comp_id):
    fields = {
        '8': 'FIX.4.2',
        '35': msg_type,
        '49': sender_comp_id,
        '56': target_comp_id,
        '34': '2',  # Example sequence number
        '52': time.strftime("%Y%m%d-%H:%M:%S.000"),
        '10': '000'
    }
    message = build_fix_message(fields)
    fields['9'] = str(len(message) - 7)
    message = build_fix_message(fields)
    fields['10'] = calculate_checksum(message)
    return build_fix_message(fields)


if __name__ == "__main__":
    main()
