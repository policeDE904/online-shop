import sqlite3

def init_database():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER
        )
    ''')
    
    # Insert default admin user
    try:
        cursor.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)",
                      ('admin', '123', 'admin@shop.com', 1))
    except:
        pass
    
    # Insert regular users (VULNERABLE TO IDOR)
    users = [
        ('john', 'password123', 'john@email.com', 0),
        ('alice', 'alice123', 'alice@email.com', 0),
        ('bob', 'bob123', 'bob@email.com', 0),
        ('user1', '123', 'user1@test.com', 0),
        ('user2', '123', 'user2@test.com', 0)
    ]
    
    for user in users:
        try:
            cursor.execute("INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)", user)
        except:
            pass
    
    # Insert products
    products = [
        ('iPhone 15', 999.99, 'Latest Apple smartphone'),
        ('Samsung Galaxy', 799.99, 'Android flagship phone'),
        ('MacBook Pro', 1999.99, 'Apple laptop for professionals'),
        ('Gaming PC', 1499.99, 'High-end gaming computer'),
        ('Wireless Headphones', 199.99, 'Noise cancelling headphones')
    ]
    
    cursor.executemany("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", products)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn
