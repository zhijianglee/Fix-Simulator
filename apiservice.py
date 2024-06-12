# This file contains the code of flask application
# Only need to run this to start both flask application and the simulator

from flask import Flask, request, jsonify
import threading

from builder import *
from simulator import FIXSimulator

app = Flask(__name__)
fix_simulator = FIXSimulator()


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    fix_simulator.send_message(data)
    return jsonify({"status": "Message sent"})


@app.route('/orders/retrieve_orders', methods=['GET'])
def retrieve_orders():
    data = request.json
    sender_comp_id = data.get('senderCompID')


@app.route('/orders/retrieve_single_order', methods=['GET'])
def retrieve_single_order():
    data = request.json
    order_id = data.get('orderID')


@app.route('/fixmessage/parse_to_json', methods=['POST'])
def decode_fix_to_json():
    data = request.json
    fix_message_object = parse_fix_message_to_json(data.get('message'),data.get('delimiter'))
    # if has_delimiters(data.get('message')):
    #     print('Message got delimiter')
    #     fix_message_object = parse_fix_message(data.get('message'))
    # else:
    #     print('Message got no delimiter')
    #     fix_message_object = parse_fix_message_no_delimiter(data.get('message'))

    return fix_message_object


def run_flask_app():
    app.run(host='0.0.0.0', port=5001)


if __name__ == "__main__":
    simulator_thread = fix_simulator.start()
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    simulator_thread.join()
    flask_thread.join()
