from jproperties import Properties

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

# def parse_fix_message(message):
#     fields = message.split('\x01')
#     return {field.split('=')[0]: field.split('=')[1] for field in fields if '=' in field}
delimiter = configs.get('delimiter').data


def parse_fix_message(message):
    # Split the message by the custom delimiter

    if delimiter in message:
        fields = message.split(delimiter)
    else:
        fields = message.split('\x01')

    # Create a dictionary to hold the parsed key-value pairs
    parsed_message = {}
    for field in fields:
        if '=' in field:
            key, value = field.split('=', 1)  # Split on the first '=' only
            parsed_message[key] = value
    return parsed_message


# Need to add in all your expected keys
def parse_fix_message_no_delimiter(message):
    keys = ["108", "8", "9", "6", "14", "20", "10", "30", "32", "35", "38", "39", "34", "49", "50", "52", "56", "58",
            "115", "1", "11",
            "15",
            "21", "22",
            "38", "40", "44", "48", "54", "55", "57", "59", "60", "84", "100", "583", "107", "196", "10", "75",
            "6", "7", "8", "9", "17", "31", "32", "37", "39", "43", "97", "150", "151", "100", "123", "128",
            "192", "12335", "151", "150", "98", "141"]

    parsed_message = {}
    while message:
        for key in keys:
            if message.startswith(key + "="):
                message = message[len(key) + 1:]
                value = ""
                while message and not any(message.startswith(k + "=") for k in keys):
                    value += message[0]
                    message = message[1:]
                parsed_message[key] = value
                break
    return parsed_message


def has_delimiters(message):
    return '\x01' in message


def build_fix_message_no_delimiter(fields):
    return ''.join(f"{key}={value}" for key, value in fields.items())


def calculate_body_length(fields):
    body_fields = {k: v for k, v in fields.items() if k not in ('8', '9', '10')}
    body = '\x01'.join(f"{key}={value}" for key, value in body_fields.items()) + '\x01'
    return len(body)


def calculate_checksum(message):
    checksum = sum(ord(char) for char in message) % 256
    return str(checksum).zfill(3)


def build_fix_message(fields):
    # Calculate body length
    body_length = calculate_body_length(fields)
    fields['9'] = str(body_length)

    # Build the message with BodyLength included
    message_with_length = '\x01'.join(f"{key}={value}" for key, value in fields.items()) + '\x01'

    # Calculate the CheckSum
    checksum = calculate_checksum(message_with_length)
    fields['10'] = checksum

    # Finalize the message with CheckSum included
    final_message = '\x01'.join(f"{key}={value}" for key, value in fields.items()) + '\x01'

    return final_message
