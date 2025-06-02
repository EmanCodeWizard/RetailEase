from flask import Flask, request, session, redirect, url_for, send_from_directory, jsonify,render_template,flash
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

# Function to generate a unique customer ID
def generate_customer_id():
    # Get the last customer ID from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT MAX(CUSTOMER_ID) FROM dbo.CUSTOMER"
    cursor.execute(query)
    result = cursor.fetchone()
    last_customer_id = result[0] if result[0] else 18148

    # Generate a new customer ID as a sequence of random numbers
    new_customer_id = last_customer_id + random.randint(1, 100)
    return new_customer_id

# Function to add a customer to the database
def add_customer(CUSTOMER_ID, EMAIL, FIRST_NAME, LAST_NAME, PHONE_NUMBER, COUNTRY):
    print("Establishing database connection...")
    conn = get_db_connection()
    if not conn:
        print("Error connecting to the database")
        return False
    try:
        print("Connection established. Executing query...")
        cursor = conn.cursor()
        query = """
            INSERT INTO dbo.CUSTOMER (CUSTOMER_ID, EMAIL, FIRST_NAME, LAST_NAME, PHONE_NUMBER, COUNTRY)
            VALUES (?,?,?,?,?,?)
        """
        print("Query:", query)
        cursor.execute(query, (CUSTOMER_ID, EMAIL, FIRST_NAME, LAST_NAME, PHONE_NUMBER, COUNTRY))
        print("Query executed successfully.")
        conn.commit()
        print("Data inserted successfully")
        return True
    except pyodbc.Error as e:
        print("Error adding new customer:", str(e))
        return False
    finally:
        print("Closing database connection...")
        conn.close()

@app.route('/')
def index():
    return redirect(url_for('customer_form'))  # Redirect to a unique route

@app.route('/customer', methods=['GET', 'POST'])
def customer_form():
    if request.method == 'POST':
        # Generate a unique customer ID
        customer_id = generate_customer_id()

        # Get the form data
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        phone_number = request.form['phone-number']
        email = request.form['Email']
        country = request.form['country']

        # Log the form data
        print(f"Received form data: Customer_ID={customer_id}, First_Name={first_name}, Last_Name={last_name}, Phone_Number={phone_number}, Email={email}, Country={country}")

        # Insert the data into the dbo.CUSTOMER table
        if add_customer(customer_id, email, first_name, last_name, phone_number, country):
            # Create a session for the user
            session['email'] = email
            return redirect(url_for('buttons'))
        else:
            return "An error occurred while registering. Please try again."

    return send_from_directory('static', 'customer.html')

@app.route('/buttons')
def buttons():
    return send_from_directory('static', 'buttons.html')

# Function to insert data into dbo.REGISTERED table
def insert_registered_user(password, registration_date):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO dbo.REGISTERED (PASSWORD, REGISTRATION_DATE)
            VALUES (?, ?)
        """
        cursor.execute(query, (password, registration_date))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error inserting registered user: {str(e)}")
        return False
    finally:
        conn.close()

@app.route('/registered_user', methods=['POST'])
def registered_user():
    password = request.form['password']
    registration_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if insert_registered_user(password, registration_date):
        return "Registered user inserted successfully!"
    else:
        return "Error inserting registered user."

# Function to insert data into dbo.NOT_REGISTERED table
def insert_not_registered_user(session_id, order_history):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO dbo.NOT_REGISTERED (SESSION_ID, ORDER_HISTORY)
            VALUES (?, ?)
        """
        cursor.execute(query, (session_id, order_history))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error inserting not registered user: {str(e)}")
        return False
    finally:
        conn.close()

@app.route('/not_registered_user', methods=['POST'])
def not_registered_user():
    session_id = request.form['session_id']
    order_history = request.form['order_history']

    if insert_not_registered_user(session_id, order_history):
        return "Not registered user inserted successfully!"
    else:
        return "Error inserting not registered user."

# Function to insert data into dbo.ORDERS table
def insert_order(customer_id, order_id, quantity, amount):
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO dbo.ORDERS (CUSTOMER_ID, ORDER_ID,NUMBER_OF_PRODUCTS, TOTAL_AMOUNT)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (customer_id, order_id, quantity, amount))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error inserting order: {str(e)}")
        return False
    finally:
        conn.close()

@app.route('/order', methods=['POST'])
def order():
    try:
        customer_id = request.form['customer-id']
        order_id = request.form['order-id']
        quantity = request.form['quantity']
        amount = request.form['amount']
        if insert_order(customer_id, order_id, quantity, amount):
            return "Order placed successfully!"
        else:
            return "Error placing order."
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return f"Error placing order: {str(e)}"
    

    #SALE PRODUCT AVLAIBLE  OR NOT
@app.route('/get_product_info', methods=['GET'])
def get_product_info():
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({"error": "No product ID provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.PRODUCT_ID, s.SALE_PRODUCT, v.VOUCHER_AVALIABLE
        FROM dbo.SALEPRODUCT s
        JOIN dbo.PRODUCT p ON p.PRODUCT_ID = s.PRODUCT_ID
        LEFT JOIN dbo.VOUCHER_AVLIABALE v ON v.PRODUCT_ID = p.PRODUCT_ID
        WHERE p.PRODUCT_ID = ?
        """, product_id
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        product_info = {
            "product_id": row.PRODUCT_ID,
            "sale_product": row.SALE_PRODUCT,
            "voucher_available": row.VOUCHER_AVALIABLE
        }
        return jsonify(product_info)
    else:
        return jsonify({"error": "Product not found"}), 404
    
    #CUSTOMER INFORMATION

@app.route('/get_customer_info', methods=['GET'])
def get_customer_info():
    customer_id = request.args.get('customer_id')
    
    if not customer_id:
        return jsonify({"error": "Missing customer ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT EMAIL, Country, FIRST_NAME, LAST_NAME, PHONE_NUMBER
        FROM dbo.CUSTOMER
        WHERE CUSTOMER_ID = ?
        """, customer_id
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        customer_info = {
            "email": row.EMAIL,
            "country": row.Country,
            "first_name": row.FIRST_NAME,
            "last_name": row.LAST_NAME,
            "phone_number": row.PHONE_NUMBER
        }
        return jsonify(customer_info)
    else:
        return jsonify({"error": "Customer not found"}), 404
    
#ORDER_INFORMATION
@app.route('/get_order_info', methods=['GET'])
def get_order_info():
    order_id = request.args.get('order_id')
    
    if not order_id:
        return jsonify({"error": "Missing order ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT NUMBER_OF_PRODUCTS, TOTAL_AMOUNT, CUSTOMER_ID
        FROM dbo.[ORDERS]
        WHERE ORDER_ID = ?
        """, order_id
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        order_info = {
            "number_of_products": row.NUMBER_OF_PRODUCTS,
            "total_amount": row.TOTAL_AMOUNT,
            "customer_id": row.CUSTOMER_ID
        }
        return jsonify(order_info)
    else:
        return jsonify({"error": "Order not found"}), 404
    

    
#UPDATING AND DELETING DATA FORM CUSTOMER TABLE
@app.route('/delete_record', methods=['POST'])
def delete_record():
    customer_id = request.form['customer_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM dbo.CUSTOMER
        WHERE CUSTOMER_ID = ?
        """, customer_id
    )
    conn.commit()
    conn.close()
    
    flash('Customer record deleted successfully')
    return redirect(url_for('index'))

@app.route('/update_record', methods=['POST'])
def update_record():
    customer_id = request.form['customer_id']
    new_email = request.form['email']
    new_phone_number = request.form['phone_number']
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE dbo.CUSTOMER
        SET EMAIL = ?, PHONE_NUMBER = ?
        WHERE CUSTOMER_ID = ?
        """, (new_email, new_phone_number, customer_id)
    )
    conn.commit()
    conn.close()
    
    flash('Customer record updated successfully')
    return redirect(url_for('index'))



#GIVING INVOICE AT THE END
@app.route('/get_payment_info', methods=['GET'])
def get_payment_info():
    customer_id = request.args.get('customer_id')
    
    if not customer_id:
        return jsonify({"error": "Missing customer ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT PAYMENT_ID, PAYMENT, INVOICE, CUSTOMER_ID, ORDER_ID
        FROM dbo.PAYMENT
        WHERE CUSTOMER_ID = ?
        """, customer_id
    )
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        payment_info = []
        for row in rows:
            payment_info.append({
                "payment_id": row.PAYMENT_ID,
                "payment": row.PAYMENT,
                "invoice": row.INVOICE,
                "customer_id": row.CUSTOMER_ID,
                "order_id": row.ORDER_ID
            })
        return jsonify(payment_info)
    else:
        return jsonify({"error": "No payments found for the given customer ID"}), 404


if __name__ == '__main__':
    app.run(debug=True)