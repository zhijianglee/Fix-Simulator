import json

import requests
import re
from bs4 import BeautifulSoup
from jproperties import Properties

from quotes_getter import get_google_code

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

# Load the JSON file
with open("exchanges.json", "r") as file:
    exchanges = json.load(file)  # Assuming it's a list of dictionaries


# URL of a stock page on Google Finance
url = "https://www.google.com/finance/quote/UBSG:"+get_google_code(exchanges, "S")
print(url)
# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract stock price (modify selector based on the current page structure)
price = soup.find('div', class_="YMlKec fxKbKc").text
stock_name=soup.find('div',class_="zzDege").text
cleaned_price = re.sub(r"[^\d.]", "", price)
print(f"Stock Price: {cleaned_price}")
print(stock_name)