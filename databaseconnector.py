import oracledb
from flask import json
from jproperties import Properties

configs = Properties()
with open('simulator.properties', 'rb') as config_file:
    configs.load(config_file)

# Define your connection parameters
username = configs.get('db_username').data
password = configs.get('db_password').data
dsn = configs.get('dsn').data  # Replace with your actual hostname, port, and service name
sid = configs.get('sid').data
hostname = configs.get('hostname').data
port = configs.get('port').data

conn = oracledb.connect(user=username, password=password, sid=sid, host=hostname, port=port)
with conn.cursor() as cur:
    cur.execute("SELECT 'Hello World!' FROM dual")
    res = cur.fetchall()
    print(res)
    # Clean up


def get_data_from_db(query):
    connection = oracledb.connect(user=username, password=password, dsn=dsn)
    # Create a cursor
    cursor = connection.cursor()

    # Execute the SQL query
    cursor.execute(query)

    # Fetch the column names
    columns = [col[0] for col in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    result = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        result.append(row_dict)

    # Convert the result to a JSON object
    json_result = json.dumps(result, indent=4)

    # Print or use the JSON result
    print(json_result)

    # Clean up
    cursor.close()
    connection.close()
