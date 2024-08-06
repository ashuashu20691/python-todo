from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
import os
import configparser

app = Flask(__name__)

# Read configuration from config.cfg
config = configparser.ConfigParser()
config.read('config.cfg')

# Oracle database configuration
username = config['database']['USER']
password = config['database']['PASSWORD']
dsn = config['database']['TNS_SERVICE_NAME']
wallet_path = config['database']['TNS_ADMIN']
tns_descriptor = "(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.ap-mumbai-1.oraclecloud.com))(connect_data=(service_name=us3a7wx6ev7txi4_testcloneautomatecicdqa_tp.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"


# Set the TNS_ADMIN environment variable to the wallet directory path
os.environ['TNS_ADMIN'] = wallet_path

# Attempt to connect to the database using cx_Oracle directly
try:
    with cx_Oracle.connect(user=username, password=password, dsn=dsn) as connection:
        print("Connected to the database successfully.")
        # Retrieve the actual DSN used for the connection
        actual_dsn = connection.dsn

        # Execute a query to retrieve data from a table
        cursor = connection.cursor()
        cursor.execute("SELECT id, category, amount FROM expenses")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")

except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Error connecting to the database: {error.message}")
    exit(1)

# Formulate the Database URI for SQLAlchemy using the actual DSN
DB_URI = f"oracle+cx_oracle://{username}:{password}@{tns_descriptor}?encoding=UTF-8&nencoding=UTF-8"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Test the SQLAlchemy connection
try:
    with db.engine.connect() as connection:
        print("Connected to the database with SQLAlchemy successfully.")
except Exception as e:
    print(f"Error connecting to the database with SQLAlchemy: {e}")
    exit(1)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

