# Defining global list to store fix messages that are sent out
global_list = []

global_seq_num = 1


def retrieve_messages(begin_seq_no, end_seq_no, message_store):
    # Assuming message_store is a list of messages with their sequence numbers
    return [msg for seq, msg in message_store if begin_seq_no <= seq <= end_seq_no]


def store_message(seq_no, message):
    global_list.append((seq_no, message))
