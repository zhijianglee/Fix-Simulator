import json
from datetime import datetime, timedelta

import pytz

with open("exchanges.json", "r") as file:
    exchanges = json.load(file)  # Assuming it's a list of dictionaries

closing_exchanges = []
# Get current time in UTC
current_time_utc = datetime.utcnow().replace(tzinfo=pytz.utc)



def get_closing_exchanges():
    for exchange in exchanges:
        # Get exchange time zone
        exchange_tz = pytz.timezone(exchange['time_zone'])

        # Get current time in exchange's time zone
        current_time_local = current_time_utc.astimezone(exchange_tz)

        # Get exchange closing time
        closing_time_str = exchange['closing_time']
        closing_time = datetime.strptime(closing_time_str, "%H:%M").time()

        # Allow a 2-minute window after the closing time
        closing_time_with_buffer = (datetime.combine(datetime.today(), closing_time) + timedelta(minutes=2)).time()

        # Check if current time is within the closing time window
        if closing_time <= current_time_local.time() <= closing_time_with_buffer:
            closing_exchanges.append(exchange['reuters_exchange_mnemonic'])

    print(closing_exchanges)


get_closing_exchanges()