import sqlite3
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(error=None):
    db = g.pop("db", None)
    if db is not None: db.close()

def init_app(app): app.teardown_appcontext(close_db)

def init_db():
    db=get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT NOT NULL,
      price REAL NOT NULL CHECK(price>=0),category TEXT NOT NULL,image TEXT NOT NULL,
      stock INTEGER NOT NULL DEFAULT 0 CHECK(stock>=0),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    db.commit()

def seed_db():
    db=get_db()
    if db.execute("SELECT COUNT(*) FROM products").fetchone()[0]: return
    rows=[
    ("Studio Wireless Headphones","Comfortable over-ear headphones with clear sound, cushioned ear pads and long battery life.",2499,"Electronics","headphones.svg",18),
    ("Everyday Smart Watch","A lightweight smartwatch concept with activity tracking, notifications and a bright touch display.",3299,"Electronics","watch.svg",12),
    ("Minimal Desk Lamp","A modern compact desk lamp for focused study sessions and workspaces.",1199,"Home","lamp.svg",25),
    ("Classic Canvas Backpack","An everyday backpack with a spacious compartment, useful pockets and comfortable straps.",1599,"Accessories","backpack.svg",9),
    ("Ceramic Coffee Mug","A durable ceramic mug with a simple design and comfortable handle.",399,"Home","mug.svg",40),
    ("Mechanical Keyboard","A compact mechanical keyboard for comfortable typing, coding and productive desk setups.",2799,"Electronics","keyboard.svg",14),
    ("Reusable Water Bottle","A reusable stainless-steel bottle for college, work or outdoor use.",699,"Accessories","bottle.svg",30),
    ("Notebook Set","Ruled notebooks for class notes, project planning and daily lists.",249,"Stationery","notebook.svg",50)]
    db.executemany("INSERT INTO products(name,description,price,category,image,stock) VALUES(?,?,?,?,?,?)",rows); db.commit()

def ensure_part23_schema():
    db=get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS carts(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS cart_items(id INTEGER PRIMARY KEY AUTOINCREMENT, cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE, product_id INTEGER NOT NULL REFERENCES products(id), quantity INTEGER NOT NULL CHECK(quantity>0), UNIQUE(cart_id,product_id));
    """)
    db.commit()
