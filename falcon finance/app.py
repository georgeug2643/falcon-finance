from flask import Flask, request, redirect, render_template
from flask_mysqldb import MySQL
import os
from flask import session, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kofi@2003'
app.config['MYSQL_DB'] = 'falcon_finance'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/receipts'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/submit-payment', methods=['POST'])
def submit_payment():
    amount = request.form['amount']
    payment_method = request.form['payment_method']
    txn_id = request.form['txn_id']
    receipt = request.files['receipt']
    filename = None
    if receipt:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], receipt.filename)
        receipt.save(filename)
    # For demo, user_id is hardcoded. Use session for real login.
    user_id = 1
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, date_submitted, payment_method, txn_id, receipt)
        VALUES (%s, %s, NOW(), %s, %s, %s)
    """, (user_id, amount, payment_method, txn_id, filename))
    mysql.connection.commit()
    cursor.close()
    flash('Payment submitted successfully!')
    return redirect('/homepage')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    contact = request.form['contact']
    username = request.form['username']
    password = request.form['password']
    dp = request.files['dp']
    dp_filename = None
    if dp:
        dp_filename = os.path.join('static/dp', dp.filename)
        os.makedirs('static/dp', exist_ok=True)
        dp.save(dp_filename)
    hashed_password = generate_password_hash(password)
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO users (name, contact, username, password, dp)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, contact, username, hashed_password, dp_filename))
    mysql.connection.commit()
    cursor.close()
    flash('Signup successful! Please log in.')
    return redirect('/index')

app.secret_key = 'your_secret_key'  # Needed for session management

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return redirect('/homepage')
    else:
        flash('Invalid username or password')
        return redirect('/index')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/homepage')
def homepage():
    if 'user_id' not in session:
        return redirect('/index')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, contact, username, dp FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    if user:
        user_data = {
            'name': user[0],
            'contact': user[1],
            'username': user[2],
            'dp': user[3]
        }
    else:
        user_data = {'name': '', 'contact': '', 'username': '', 'dp': ''}
    return render_template('homepage.html', user=user_data)

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect('/index')
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT amount, date_submitted, payment_method
        FROM transactions
        WHERE user_id = %s
        ORDER BY date_submitted DESC
    """, (session['user_id'],))
    transactions = cursor.fetchall()
    cursor.close()
    total_paid = sum([float(txn[0]) for txn in transactions])
    return render_template('transactions.html', transactions=transactions, total_paid=total_paid)

@app.route('/test')
def test():
    return "Flask is working!"

@app.route('/')
def root():
    return redirect('/index')

if __name__ == '__main__':
    app.run(debug=True)