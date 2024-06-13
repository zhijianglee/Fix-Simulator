from jproperties import Properties
import json

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


def parse_fix_message_to_json(message, delimiter='^A'):
    # Step 1: Replace the custom delimiter with the standard delimiter
    standard_delimiter = '\x01'
    message = message.replace(delimiter, standard_delimiter)

    # Step 2: Split the message using the standard delimiter
    fields = message.split(standard_delimiter)

    # Step 2: Split the message using the standard delimiter
    fields = message.split('\x01')

    # Step 3: Convert the fields into a dictionary
    message_dict = {}
    for field in fields:
        if '=' in field:
            key, value = field.split('=', 1)  # Split only on the first '='
            message_dict[key] = value

    # Step 4: Convert the dictionary into a JSON object
    message_json = json.dumps(message_dict, indent=4)

    return message_json


# def parse_fix_message(message):
#     fields = message.split('\x01')
#     msg_dict = {}
#     for field in fields:
#         if field:
#             tag, value = field.split('=')
#             msg_dict[tag] = value
#     return msg_dict


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
