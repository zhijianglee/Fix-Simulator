import oracledb
from flask import json, jsonify
from jproperties import Properties

from write_to_log import output_to_file_log_debug

configs = Properties()
with open('db.properties', 'rb') as config_file:
    configs.load(config_file)

# Define your connection parameters
fryingpan = configs.get('db_username').data
saucepan = configs.get('db_password').data
sn = configs.get('sn').data
sid = configs.get('sid').data
hostname = configs.get('hostname').data
port = configs.get('port').data


def make_db_insert(columns, values):
    # Handle None values and format the values list for SQL query
    formatted_values = [
        f"'{value}'" if value is not None else 'NULL' for value in values
    ]

    # Construct the SQL query
    insert_query = f"""
    INSERT INTO SIMULATOR_RECORDS ({', '.join(columns)})
    VALUES ({', '.join(formatted_values)})
    """

    doInsert(insert_query)


def doInsert(query):
    try:
        connection = oracledb.connect(user=fryingpan, host=hostname, password=saucepan, service_name=sn, port=port)
        cursor = connection.cursor()
        output_to_file_log_debug(query)
        cursor.execute(query)
        connection.commit()
        output_to_file_log_debug("Data inserted successfully.")
    except oracledb.DatabaseError as e:
        print(f"Database error: {e}")


def getSingleResultFromDB(query,backup_query=None):
    try:
        connection = oracledb.connect(user=fryingpan, host=hostname, password=saucepan, service_name=sn, port=port)
        cursor = connection.cursor()
        output_to_file_log_debug(query)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            output_to_file_log_debug(result)
            return result[0]
        else:
            return 'No data found'

    except Exception as e:
        print(f"Error: {e}")


def getResultFromDB(query):
    connection = oracledb.connect(user=fryingpan, host=hostname, password=saucepan, service_name=sn, port=port)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append(dict(zip([column[0] for column in cursor.description], row)))

        cursor.close()
        connection.close()

        # Return the query result as JSON
        return jsonify(result), 200

    except oracledb.DatabaseError as e:
        # If an error occurs during the query execution, return an error response
        return jsonify({'error': 'An error occurred while executing the query'}), 500
