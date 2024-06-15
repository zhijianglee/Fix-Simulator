import json


def save_sequence_number(sequence_number):
    with open('sequence_number.json', 'w') as file:
        json.dump(sequence_number, file)


def save_message_log(message_log):
    with open('message_log.json', 'a') as file:
        json.dump(message_log, file)
