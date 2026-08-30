from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
import sqlite3
import re
#by Austin Leach

app = Flask(__name__)
app.secret_key = 'not_your_secret_key'

def remove_sql_keywords(input_string):
    # Define a regular expression pattern to match SQL injection patterns
    pattern = r'(\badmin\b|--|(\b(?:insert|delete|update|drop|alter)\b\s*\(\s*\)|\b(?:insert|delete|update|drop|alter|create)\b\s+.*?\s*\b(?:from|where|set)\b)|\bexec\b\s*\(@|\bcreate\s+procedure\b|\bdeclare\b|\bexec\b|\bbackup\s+database\b|\bcast\b\s*\(.*?\bexec\b|\bexec\b\s*\(.*?\bcast\b|\bselect\b.*?\bfrom\b.*?\bwhere\b|\bselect\b.*?\bfrom\b.*?\bwhere\b|\b(?:or|is|not|join|union)\b|=)'

    # Use re.sub to replace matched patterns with empty string
    filtered_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)
    print(filtered_string)

    return filtered_string

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('users.db')

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        username = remove_sql_keywords(request.form['username'])
        password = remove_sql_keywords(request.form['password'])
    
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        user = cursor.fetchone()
        db.close()

        if user:
            session['username'] = username
            return redirect('/home')
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function

# Route for the home page
@app.route('/home')
@login_required
def home():
    if 'username' in session:
        username = session['username']
        session.pop('username', None)
        return render_template('home.html', username=username)
    else:
        return redirect('/')
    
@app.errorhandler(500)
def internal_server_error(error):
    # Log the error for debugging purposes
    app.logger.error('Your input has been filtered against: %s', error)

    # Render a custom error page with a friendly message
    return render_template('login.html', error='Your input has been filtered against or the server crashed. Hopefully not the second'), 500

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
