# Defining global list to store fix messages that are sent out
global_list = []

global_seq_num = 1


def retrieve_messages(begin_seq_no, end_seq_no, message_store):
    print('Getting messages')
    retrieved_messages = []
    for seq, msg in message_store:
        if begin_seq_no <= seq <= end_seq_no:
            retrieved_messages.append(msg)
            print(msg)
    return retrieved_messages


def store_message(seq_no, message):
    global_list.append((seq_no, message))
