
# Introduction

This is a fix simulator using FIX 4.2 protocol built by relying on ChatGPT almost 60%. 
It has some basic functionalities such as responding to login and order requests **(covered 35=D, 35=F and 35G)**
This simulator has basic functions for basics testing. You need to configure it according to your needs </br>

This simulator also comes with a flask application containing several API endpoints. **However, only /fix message/parse_to_json and /send_message is working**. 

# Set Up

## Environment Setup
Minimum Python version is 3.9, but ideally is 3.12
Oracle DB is required, or at least a database, it can be MSSQL, MariaDB. However, you need to work out on code implementation in databaseconnector.py


## Properties Files
There are two properties file you need to configure to get things started.
* simulator.properties
* db.properties

### simulator.properties
Simulator.properties containing list of configurable properties. 

Change the simulator_comp_id and ensure that your client fix adapter is pointing to the correct one.

simulator.properties has been configured with default values. You may review them and change them according to your 
preferences. Comments exists in the property file contains tips on how to set the value. 

The value of market_price_source has been defaulted to 'GOOGLE' which will obtain latest delayed quote from Google Finance. 

You can switch it to 'DB' if you want to obtain the last done price from your internal DB. 

Implementation of the logic to obtain last done price and bid price is in quotes_getter.py

For Example: If This is your query to obtain last done price

SELECT LAST_DONE_PRICE FROM COUNTER WHERE COUNTER_CODE='C6L' or SELECT LAST_DONE_PRICE FROM COUNTER WHERE FEED_COUNTER_CODE='C6L.SI'

Then this is how you should configure those values in properties file
market_price_db_source_table=COUNTER
market_stock_column1=FEED_COUNTER_CODE
market_stock_column2=COUNTER_CODE
market_last_price_column=LAST_DONE_PRICE

This is the same for bid price as well. 


### db.properties

You will need to create db.properties file containing the below items.

* db_username=fixsim
* db_password=fixsim123
* sn=
* sid=XE
* hostname=localhost
* port=1521


You will need to create a user (table space) and grant SELECT, CREATE AND UPDATE query to that user.
After that login as that user and crete required table using the DDL attached in this directory.


# Running the simulator

1. Ensure the below modules are being installed Refer to requirements.txt
2. Start the simulator by using python3 apiservice.py 7418 5031

   7418 is binding port for fix message
   5031 is the port for API request

   Please use one port for one fix session


# Using FIX Server Simulator API endpoints

## Using /send_message

You can use this to send fix message to connected client by passing in your desired tags in a json object form

### These tags will be automatically added. Do not include them

49,17,37,52,60,34,10


# Known Bugs and Pull Requests are Welcomed
1. Sequence number will be out of sync after some time running the simulator
2. The fix message return from the simulator might not get recognized by your fix adapter / client.
3. No multithreading capability. One port can only serve one comp id



# Working Examples / Tests


### **Order Submissions**

![img.png](img.png)

