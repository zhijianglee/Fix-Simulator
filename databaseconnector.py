import oracledb
from flask import json, jsonify
from jproperties import Properties

configs = Properties()
with open('db.properties', 'rb') as config_file:
    configs.load(config_file)

# Define your connection parameters
username = configs.get('db_username').data
password = configs.get('db_password').data
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
        connection = oracledb.connect(user=username, host=hostname, password=password, sid=sid, port=port)
        cursor = connection.cursor()
        print(query)
        cursor.execute(query)
        connection.commit()
        print("Data inserted successfully.")
    except oracledb.DatabaseError as e:
        print(f"Database error: {e}")


def getSingleResultFromDB(query):
    try:
        connection = oracledb.connect(user=username, host=hostname, password=password, sid=sid, port=port)
        cursor = connection.cursor()
        print(query)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            return result[0]
        else:
            return 'No data found'

    except Exception as e:
        print(f"Error: {e}")


def getResultFromDB(query):
    connection = oracledb.connect(user=username, host=hostname, password=password, sid=sid, port=port)
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
