def parse_fix_message(message):
    fields = message.split('\x01')
    return {field.split('=')[0]: field.split('=')[1] for field in fields if '=' in field}


def build_fix_message(fields):
    return '\x01'.join(f"{key}={value}" for key, value in fields.items()) + '\x01'


def calculate_checksum(message):
    checksum = sum(ord(char) for char in message) % 256
    return str(checksum).zfill(3)
