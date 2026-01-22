from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, add_user, get_user, add_book, get_all_books, get_user_books
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database
init_db()

# Sample books data
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
    return render_template('index.html', books=sample_books[:6])

@app.route('/browse')
def browse():
    books = get_all_books()
    all_books = sample_books + books
    return render_template('browse.html', books=all_books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if get_user(email):
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        add_user(username, email, hashed_password)
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user(email)
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    user_books = get_user_books(session['user_id'])
    return render_template('dashboard.html', books=user_books)

@app.route('/sell', methods=['POST'])
def sell_book():
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    title = request.form['title']
    author = request.form['author']
    price = float(request.form['price'])
    condition = request.form['condition']
    
    add_book(session['user_id'], title, author, price, condition)
    flash('Book listed successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)