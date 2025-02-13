from flask import Flask, request, redirect, session
from flask import render_template_string
import time
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simulated database of users (username: BankAccount instance)
users_db = {}

class BankAccount:
    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password
        self.balance = 0.0
        self.transactions = []

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.transactions.append(f"{timestamp} - Deposited ${amount:.2f}")
            return f"Deposited ${amount:.2f}.", True
        return "Deposit amount must be positive!", False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.transactions.append(f"{timestamp} - Withdrew ${amount:.2f}")
            return f"Withdrew ${amount:.2f}.", True
        elif amount > self.balance:
            return "Insufficient balance!", False
        return "Withdrawal amount must be positive!", False

    def check_balance(self):
        return f"Current balance: ${self.balance:.2f}"

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Banking System</title>
    <style>
        body { background-color: #f4f4f4; font-family: Arial, sans-serif; text-align: center; }
        .container { width: 50%; margin: auto; background: white; padding: 20px; border-radius: 10px; }
        input, button { margin: 10px; padding: 10px; }
        .message { transition: opacity 1s; }
    </style>
    <script>
        setTimeout(function() {
            var msg = document.getElementById('message');
            if (msg) { msg.style.opacity = '0'; setTimeout(() => msg.remove(), 1000); }
        }, 3000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Banking System</h1>
        {% if not session.username %}
            <h2>Signup</h2>
            <form method="post" action="/signup">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign Up</button>
            </form>
            <h2>Login</h2>
            <form method="post" action="/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <h2>Welcome, {{ session.username }}</h2>
            <form method="post" action="/dashboard">
                <input type="number" name="amount" placeholder="Amount">
                <button type="submit" name="action" value="Deposit">Deposit</button>
                <button type="submit" name="action" value="Withdraw">Withdraw</button>
            </form>
            <form method="post" action="/dashboard">
                <button type="submit" name="action" value="Check Balance">Check Balance</button>
                <button type="submit" name="action" value="Cancel">Cancel</button>
            </form>
            <form method="post" action="/dashboard">
                <button type="submit" name="action" value="Transactions">View Transactions</button>
                <button type="submit" name="action" value="Cancel">Cancel</button>
            </form>
            {% if message %}<p id="message" class="message">{{ message }}</p>{% endif %}
            {% if balance_message %}<p id="balance_message">{{ balance_message }}</p>{% endif %}
            {% if transactions %}
                <h3>Transaction History</h3>
                <ul>
                    {% for transaction in transactions %}
                        <li>{{ transaction }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
            <a href="/logout">Logout</a>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    if username in users_db:
        return "Username already exists! Try a different one."
    users_db[username] = BankAccount(request.form['name'], username, request.form['password'])
    session['username'] = username
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users_db and users_db[username].password == password:
        session['username'] = username
        return redirect('/')
    return "Invalid username or password!"

@app.route('/dashboard', methods=['POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/')
    account = users_db[session['username']]
    action = request.form['action']
    if action == "Cancel":
        return redirect('/')
    amount = float(request.form.get('amount', 0)) if 'amount' in request.form else 0
    message = ""
    balance_message = ""
    transactions = []
    if action == "Deposit":
        message, _ = account.deposit(amount)
    elif action == "Withdraw":
        message, _ = account.withdraw(amount)
    elif action == "Check Balance":
        balance_message = account.check_balance()
    elif action == "Transactions":
        transactions = account.transactions
    return render_template_string(html_template, session=session, message=message, balance_message=balance_message, transactions=transactions)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
