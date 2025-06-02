from flask import Flask, request, session, redirect, url_for, send_from_directory, render_template, jsonify
import pyodbc
import random
import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_here'

# Define the database connection parameters
server = r'DESKTOP-4DSCR2G\SQLEXPRESS01'  # Use raw string to handle backslashes
database = 'DBMSRS'
username = ''
password = ''

# Function to create a connection to the database
def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            'Trusted_Connection=yes;'
        )
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to the database: {str(e)}")
        return None

# Function to insert data into dbo.ORDERS table
def insert_order(customer_id, order_id, quantity, amount):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO dbo.ORDERS (CustomerID, OrderID, Quantity, Amount)
        VALUES (?, ?, ?, ?)
        '''
        cursor.execute(insert_query, (customer_id, order_id, quantity, amount))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error inserting order: {e}")
        return False
    finally:
        conn.close()

@app.route('/')
def index():
    return redirect(url_for('order'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        order_id = request.form['order_id']
        quantity = request.form['quantity']
        amount = request.form['amount']

        if insert_order(customer_id, order_id, quantity, amount):
            return "Order submitted successfully!"
        else:
            return "Error submitting order."

    return send_from_directory('static', 'order.html')

@app.route('/buttons')
def buttons_page():
    return send_from_directory('static', 'buttons.html')

if __name__ == '__main__':
    app.run(debug=True)
