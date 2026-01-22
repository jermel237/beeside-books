from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static',
            static_url_path='/static')

app.secret_key = 'beeside-secret-key-2024'

# Database path
if os.path.exists('/tmp'):
    DB_PATH = '/tmp/beesidebooks.db'
else:
    DB_PATH = 'beesidebooks.db'

# Database functions
def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL,
            condition TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Sample books
sample_books = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": 8.99, "condition": "Good", "image": "📚"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "price": 7.50, "condition": "Like New", "image": "📖"},
    {"title": "1984", "author": "George Orwell", "price": 6.99, "condition": "Good", "image": "📕"},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "price": 5.99, "condition": "Acceptable", "image": "📗"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "price": 9.50, "condition": "Like New", "image": "📘"},
    {"title": "Harry Potter", "author": "J.K. Rowling", "price": 12.99, "condition": "New", "image": "📙"},
]

@app.route('/')
def index():
    return render_template('index.html', books=sample_books)

@app.route('/browse')
def browse():
    return render_template('browse.html', books=sample_books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect('/register')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                          (username, email, password))
            conn.commit()
            conn.close()
            flash('Account created! Please login.', 'success')
            return redirect('/login')
        except:
            flash('Email already exists!', 'error')
            return redirect('/register')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Welcome back!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password!', 'error')
            return redirect('/login')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect('/login')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE user_id = ?', (session['user_id'],))
    books = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', books=books)

@app.route('/sell', methods=['POST'])
def sell_book():
    if 'user_id' not in session:
        return redirect('/login')
    
    title = request.form['title']
    author = request.form['author']
    price = float(request.form['price'])
    condition = request.form['condition']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (user_id, title, author, price, condition) VALUES (?, ?, ?, ?, ?)',
                  (session['user_id'], title, author, price, condition))
    conn.commit()
    conn.close()
    
    flash('Book listed!', 'success')
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out!', 'success')
    return redirect('/')

# This is required for Vercel
if __name__ == '__main__':
    app.run(debug=True)