from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from database import init_database, get_db_connection
import json

app = Flask(__name__)
app.secret_key = 'vulnerable_secret_key'

# Initialize database
init_database()

# VULNERABLE LOGIN - SQL Injection possible
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABILITY: SQL Injection
        conn = get_db_connection()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                return redirect(url_for('shop'))
            else:
                return "Invalid credentials! Try admin/123 or user1/123"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            conn.close()
    
    return render_template('login.html')

# VULNERABLE SHOP PAGE - IDOR possible
@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    return render_template('shop.html', products=products, username=session['username'])

# VULNERABLE API - No authentication
@app.route('/api/users')
def api_users():
    # VULNERABILITY: No authentication - exposes all users
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, is_admin FROM users').fetchall()
    conn.close()
    
    users_list = [dict(user) for user in users]
    return jsonify(users_list)

# VULNERABLE USER PROFILE - IDOR
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    # VULNERABILITY: IDOR - can access any user's data
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, email, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return f"""
        <h1>User Profile (IDOR VULNERABLE)</h1>
        <p>User ID: {user['id']}</p>
        <p>Username: {user['username']}</p>
        <p>Email: {user['email']}</p>
        <p>Admin: {user['is_admin']}</p>
        <a href="/shop">Back to Shop</a>
        """
    return "User not found"

# VULNERABLE ADMIN PANEL - No proper authorization
@app.route('/admin')
def admin_panel():
    # VULNERABILITY: No proper admin check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Check if user is admin (but easily bypassable)
    user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user and user['is_admin']:
        users = conn.execute('SELECT * FROM users').fetchall()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return render_template('admin.html', users=users, products=products)
    else:
        conn.close()
        return "Access denied! You need to be admin. Try accessing /admin directly or change your user ID."

# VULNERABLE PRODUCT PURCHASE
@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # VULNERABILITY: No product existence check
    conn.execute('INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)',
                (session['user_id'], product_id, 1))
    conn.commit()
    
    product = conn.execute('SELECT name FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product:
        return f"Successfully purchased {product['name']}! <a href='/shop'>Continue Shopping</a>"
    return "Product not found"

# VULNERABLE SEARCH - SQL Injection
@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # VULNERABILITY: SQL Injection in search
    conn = get_db_connection()
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
    
    try:
        products = conn.execute(sql).fetchall()
        results = [dict(product) for product in products]
        conn.close()
        return jsonify(results)
    except Exception as e:
        return f"Error: {str(e)}"

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
