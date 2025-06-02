import pyodbc
from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_here'

# Define the database connection parameters
server = r'DESKTOP-4DSCR2G\SQLEXPRESS01'
database = 'DBMSRS'
username = ''
password = ''

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

def add_registered(PASSWORD, REGISTRATION_DATE):
    print("Establishing database connection...")
    conn = get_db_connection()
    if not conn:
        print("Error connecting to the database")
        return False
    try:
        print("Connection established. Executing query...")
        cursor = conn.cursor()
        query = """
            INSERT INTO dbo.REGISTERED (PASSWORD, REGISTRATION_DATE)
            VALUES (?, ?)
        """
        print("Query:", query)
        cursor.execute(query, (PASSWORD, REGISTRATION_DATE))
        print("Query executed successfully.")
        conn.commit()
        print("Data inserted successfully")
        return True
    except pyodbc.Error as e:
        print("Error adding new registered user:", str(e))
        return False
    finally:
        print("Closing database connection...")
        conn.close()

@app.route('/', endpoint='index')
def index():
    return redirect(url_for('registered_user'))

@app.route('/registered_user', methods=['GET', 'POST'], endpoint='registered_user')
def registered_user():
    if request.method == 'POST':
        PASSWORD = request.form.get('Password')
        REGISTRATION_DATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Received form data: Password={PASSWORD}, Registration_Date={REGISTRATION_DATE}")

        if PASSWORD is None:
            print("Password is missing from the form data")
            return "Password is missing from the form data"

        if add_registered(PASSWORD, REGISTRATION_DATE):
            return redirect(url_for('home'))
        else:
            return "An error occurred while registering. Please try again."

    return render_template('registered_user.html')

@app.route('/home', endpoint='home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
