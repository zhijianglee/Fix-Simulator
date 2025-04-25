# This file contains the code of flask application
# Only need to run this to start both flask application and the simulator
import asyncio
import logging
import sys

import requests
from flask import Flask, request, jsonify
import threading

from builder import *
from simulator import FIXSimulator
import random

app = Flask(__name__)
fix_simulator = FIXSimulator()

flask_port_to_use = random.randrange(5002, 5055)




@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    fix_simulator.send_custom_message(data, simulator.conn)
    return jsonify({"status": "Message sent"})


@app.route('/orders/retrieve_orders', methods=['GET'])
def retrieve_orders():
    data = request.json
    sender_comp_id = data.get('senderCompID')


@app.route('/orders/retrieve_single_order', methods=['GET'])
def retrieve_single_order():
    data = request.json
    order_id = data.get('orderID')




@app.route('/fix message/parse_to_json', methods=['POST'])
def decode_fix_to_json():
    data = request.json
    fix_message_object = parse_fix_message_to_json(data.get('message'), data.get('delimiter'))
    # if has_delimiters(data.get('message')):
    #     print('Message got delimiter')
    #     fix_message_object = parse_fix_message(data.get('message'))
    # else:
    #     print('Message got no delimiter')
    #     fix_message_object = parse_fix_message_no_delimiter(data.get('message'))

    return fix_message_object



def run_flask_app():
    port_to_use = flask_port_to_use
    print(port_to_use)
    app.run(host='0.0.0.0', port=port_to_use)


if __name__ == "__main__":
    # simulator_thread = fix_simulator.start()
    # flask_thread = threading.Thread(target=run_flask_app)
    # flask_thread.start()
    #
    # simulator_thread.join()
    # flask_thread.join()
    simulator_port = int(sys.argv[1])
    flask_port_to_use = int(sys.argv[2])
    simulator = FIXSimulator(port=simulator_port)

    # Start the Flask application in the main thread

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Start the FIXSimulator server in a separate thread
    # simulator_thread = threading.Thread(target=lambda: asyncio.run(simulator.run_server()))
    simulator_thread = threading.Thread(target=simulator.run_server())
    simulator_thread.start()

    flask_thread.join()
    simulator_thread.join()
