import random

import requests
import re
from bs4 import BeautifulSoup
from jproperties import Properties
import json

# Load the JSON file
with open("exchanges.json", "r") as file:
    exchanges = json.load(file)  # Assuming it's a list of dictionaries

import databaseconnector
configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)


# Retrieve google_code where reuters_exchange_mnemonic is "L"
def get_google_code(exchanges, mnemonic):
    for exchange in exchanges:
        if exchange.get("reuters_exchange_mnemonic") == mnemonic:
            return exchange.get("google_code")
    return None  # Return None if not found


market_price_source = str(configs.get('market_price_source').data)
market_price_db_source_table = str(configs.get('market_price_db_source_table').data)
market_stock_column1 = str(configs.get('market_stock_column1').data)
market_stock_column2 = str(configs.get('market_stock_column2').data)
market_bid_column = str(configs.get('market_bid_column').data)
market_last_price_column = str(configs.get('market_bid_column').data)



def get_last_price(order):
    try:
        # Default last_price
        last_price = 1

        if market_price_source == 'GOOGLE':
            try:
                # URL of a stock page on Google Finance
                url = "https://www.google.com/finance/quote/" + order.Symbol + ":" + get_google_code(exchanges, order.ExDestination)

                # Fetch the page content
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTPError if the status is not 200

                # Parse the content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract stock price (modify selector based on the current page structure)
                price = soup.find('div', class_="YMlKec fxKbKc").text
                cleaned_price = re.sub(r"[^\d.]", "", price)
                last_price = float(cleaned_price)

            except Exception as e:
                print(f"Error fetching price from Google: {e}")

        elif market_price_source == 'DB':
            try:
                # Query database for last price
                last_price = databaseconnector.getSingleResultFromDB(
                    "SELECT " + market_last_price_column + " FROM " + market_price_db_source_table +
                    " WHERE " + market_stock_column1 + "='" + order.security_id + "'"
                )

                if last_price == "No data found":
                    last_price = databaseconnector.getSingleResultFromDB(
                        "SELECT " + market_last_price_column + " FROM " + market_price_db_source_table +
                        " WHERE " + market_stock_column2 + "='" + order.Symbol + "'"
                    )

            except Exception as e:
                print(f"Error fetching price from database: {e}")

        # If no valid price was found, or an exception occurred, set a random price
        if not last_price or last_price == "No data found":
            raise ValueError("Failed to retrieve last price")

    except Exception as e:
        print(f"Fallback to random price due to error: {e}")
        last_price = round(random.uniform(10, 1000), 2)  # Random price between 10 and 1000

    return last_price



def get_bid_price(order):
    try:
        # Default bid_price
        bid_price = 1

        if market_price_source == 'GOOGLE':
            try:
                # URL of the stock on Google Finance
                url = "https://www.google.com/finance/quote/" + order.Symbol + ":" + get_google_code(exchanges, order.ExDestination)

                # Fetch the web page
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTPError if the status is not 200

                # Parse the content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract bid price (modify selector based on the current page structure)
                bid_price = soup.find('div', class_="YMlKec fxKbKc").text  # Replace with actual class
                cleaned_price = re.sub(r"[^\d.]", "", bid_price)
                bid_price = float(cleaned_price)

            except Exception as e:
                print(f"Error fetching bid price from Google: {e}")

        elif market_price_source == 'DB':
            try:
                # Query database for bid price
                bid_price = databaseconnector.getSingleResultFromDB(
                    "SELECT BID FROM COUNTER WHERE FEED_COUNTER_CODE='" + order.security_id + "'"
                )

                if bid_price == "No data found":
                    bid_price = databaseconnector.getSingleResultFromDB(
                        "SELECT BID FROM COUNTER WHERE COUNTER_CODE='" + order.Symbol + "'"
                    )

            except Exception as e:
                print(f"Error fetching bid price from database: {e}")

        # If no valid bid price was found, or an exception occurred, set a random price
        if not bid_price or bid_price == "No data found":
            raise ValueError("Failed to retrieve bid price")

    except Exception as e:
        print(f"Fallback to random bid price due to error: {e}")
        bid_price = round(random.uniform(5, 500), 2)  # Random bid price between 5 and 500

    return bid_price