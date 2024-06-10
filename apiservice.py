# This file contains the code of flask application
# Only need to run this to start both flask application and the simulator

from flask import Flask, request, jsonify
import threading

from builder import build_fix_message
from simulator import FIXSimulator

app = Flask(__name__)
fix_simulator = FIXSimulator()


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    fixmessage = build_fix_message(data)
    fix_simulator.send_message(fixmessage)
    return jsonify({"status": "Message sent"})


@app.route('/orders/retrieve_orders', methods=['GET'])
def retrieve_orders():
    data = request.json
    sender_comp_id = data.get('senderCompID')


@app.route('/orders/retrieve_single_order', methods=['GET'])
def retrieve_single_order():
    data = request.json
    order_id = data.get('orderID')


def run_flask_app():
    app.run(host='0.0.0.0', port=5001)


if __name__ == "__main__":
    simulator_thread = fix_simulator.start()
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    simulator_thread.join()
    flask_thread.join()
