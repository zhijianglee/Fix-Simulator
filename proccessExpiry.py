from datetime import datetime, timedelta
import pytz
from jproperties import Properties

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


def is_future_time_geq(time_str, timezone_str):
    """
    Check if the time 30 seconds from now in the specified timezone is greater than or equal to the given time.

    :param time_str: Time in HH:MM format (24-hour)
    :param timezone_str: Timezone name (e.g., 'America/New_York')
    :return: True if future time is >= given time, False otherwise
    """
    # Parse the input time string
    given_time = datetime.strptime(time_str, "%H:%M").time()

    # Get the current time in the specified timezone
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone)

    # Add 30 seconds to the current time
    future_time = (current_time + timedelta(seconds=30)).time()

    # Compare the future time with the given time
    return future_time >= given_time


# Example usage
time_to_check = "14:30"  # 2:30 PM
timezone_to_check = "America/New_York"

if is_future_time_geq(time_to_check, timezone_to_check):
    print(f"The time 30 seconds from now in {timezone_to_check} will be greater than or equal to {time_to_check}.")
else:
    print(f"The time 30 seconds from now in {timezone_to_check} will be less than {time_to_check}.")
