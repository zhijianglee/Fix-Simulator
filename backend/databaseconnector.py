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
    connection = None
    cursor = None
    try:
        connection = oracledb.connect(user=fryingpan, host=hostname, password=saucepan, service_name=sn, port=port)
        cursor = connection.cursor()
        output_to_file_log_debug(query)
        cursor.execute(query)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return result

    except oracledb.DatabaseError as e:
        print(f"Database error: {e}")
        return []

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
