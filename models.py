"""
Database models for Mechlands Garage.
Uses SQLite (built into Python) — no server setup needed.
"""

import os
import sqlite3
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt


# Initialize bcrypt (this is used by app.py too)
bcrypt = Bcrypt()

# Database file path — lives in data/ folder so it's backed up with other data
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'mechlands.db')


# def get_db():
#     """Get a database connection. Rows behave like dictionaries."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

def get_db():
    """
    Get a database connection.
    - timeout: wait up to 10 seconds for locks to clear before erroring
    - check_same_thread=False: allow the connection to be used across threads
      (safe because each request gets its own connection)
    - row_factory: rows behave like dictionaries
    """
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent read/write behavior
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def init_db():
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff',
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')

    # Blog posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            excerpt TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'upcoming',
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Gallery items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            caption TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Shop products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Vehicles for sale
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            mileage INTEGER,
            fuel_type TEXT,
            transmission TEXT,
            description TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'available',
            created_at TEXT NOT NULL
        )
    ''')

    # Car Specifications for Comparison
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_specs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year TEXT,
            body_type TEXT,
            engine_cc INTEGER,
            fuel_type TEXT,
            fuel_efficiency TEXT,
            reliability_score INTEGER,
            maintenance_cost TEXT,
            resale_value TEXT,
            spares_availability TEXT,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()


def create_user(email, password, full_name, role='staff'):
    """Create a new user with a hashed password. Returns the user ID or None if email exists."""
    email = email.lower().strip()
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    created_at = datetime.now().isoformat()

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (email, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)',
            (email, password_hash, full_name, role, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # Email already exists
        return None


def get_user_by_email(email):
    """Fetch a user by email. Returns dict-like row or None."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    """Fetch a user by ID. Returns dict-like row or None."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_last_login(user_id):
    """Record the last login timestamp."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET last_login = ? WHERE id = ?',
        (datetime.now().isoformat(), user_id)
    )
    conn.commit()
    conn.close()


def count_users():
    """Return total number of users. Used to check if this is a fresh install."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    row = cursor.fetchone()
    conn.close()
    return row['count'] if row else 0


# ============ USER CLASS FOR FLASK-LOGIN ============
class User(UserMixin):
    """Wraps a database row for Flask-Login compatibility."""

    def __init__(self, row):
        self.id = str(row['id'])
        self.email = row['email']
        self.full_name = row['full_name']
        self.role = row['role']
        self.created_at = row['created_at']
        self.last_login = row['last_login'] if 'last_login' in row.keys() else None

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff(self):
        return self.role in ('admin', 'staff')


# ============ SUBMISSIONS READER ============
import json

def read_submissions(limit=None):
    """
    Read all submissions from data/submissions.jsonl.
    Returns a list of dicts, newest first.
    If limit is set, returns only that many.
    """
    submissions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'submissions.jsonl')
    if not os.path.exists(submissions_path):
        return []

    submissions = []
    with open(submissions_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                submissions.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                continue

    # Sort by timestamp, newest first
    submissions.sort(key=lambda s: s.get('timestamp', ''), reverse=True)

    if limit:
        return submissions[:limit]
    return submissions


def count_submissions_by_type():
    """Return counts of each submission type."""
    submissions = read_submissions()
    counts = {}
    for s in submissions:
        t = s.get('type', 'contact')
        counts[t] = counts.get(t, 0) + 1
    return counts


# ============ CONTENT: BLOG POSTS ============

def list_blog_posts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_blog_post_by_slug(slug):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE slug = ?', (slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_blog_post_by_id(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_blog_post(slug, title, date, excerpt, body):
    now = datetime.now().isoformat()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO blog_posts (slug, title, date, excerpt, body, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (slug, title, date, excerpt, body, now, now)
        )
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        return post_id
    except sqlite3.IntegrityError:
        return None


def update_blog_post(post_id, slug, title, date, excerpt, body):
    now = datetime.now().isoformat()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE blog_posts SET slug = ?, title = ?, date = ?, excerpt = ?, body = ?, updated_at = ? WHERE id = ?',
            (slug, title, date, excerpt, body, now, post_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_blog_post(post_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blog_posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()


# ============ CONTENT: EVENTS ============

def list_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_event_by_id(event_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_event(slug, title, date, location, status, description):
    now = datetime.now().isoformat()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO events (slug, title, date, location, status, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (slug, title, date, location, status, description, now, now)
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id
    except sqlite3.IntegrityError:
        return None


def update_event(event_id, slug, title, date, location, status, description):
    now = datetime.now().isoformat()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE events SET slug = ?, title = ?, date = ?, location = ?, status = ?, description = ?, updated_at = ? WHERE id = ?',
            (slug, title, date, location, status, description, now, event_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_event(event_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()


# ============ CONTENT: GALLERY ============

def list_gallery_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gallery_items ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_gallery_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gallery_items WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_gallery_item(image, caption, category):
    now = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO gallery_items (image, caption, category, created_at) VALUES (?, ?, ?, ?)',
        (image, caption, category, now)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id


def delete_gallery_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gallery_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()


# ============ CONTENT: PRODUCTS ============

def list_products(category=None):
    conn = get_db()
    cursor = conn.cursor()
    if category:
        cursor.execute('SELECT * FROM products WHERE category = ? ORDER BY id', (category,))
    else:
        cursor.execute('SELECT * FROM products ORDER BY category, id')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# def create_product(sku, category, name, description, price):
#     now = datetime.now().isoformat()
#     try:
#         conn = get_db()
#         cursor = conn.cursor()
#         cursor.execute(
#             'INSERT INTO products (sku, category, name, description, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
#             (sku, category, name, description, price, now, now)
#         )
#         conn.commit()
#         product_id = cursor.lastrowid
#         conn.close()
#         return product_id
#     except sqlite3.IntegrityError:
#         return None

def create_product(sku, category, name, description, price):
    now = datetime.now().isoformat()
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (sku, category, name, description, price, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sku, category, name, description, price, now, now)
        )
        conn.commit()
        product_id = cursor.lastrowid
        return product_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_product(product_id, sku, category, name, description, price):
    now = datetime.now().isoformat()
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE products SET sku = ?, category = ?, name = ?, description = ?, price = ?, updated_at = ? WHERE id = ?',
            (sku, category, name, description, price, now, product_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

# ============ CAR SALES ============

def list_vehicles(status='available'):
    conn = get_db()
    try:
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT * FROM vehicles WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM vehicles ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_vehicle(vehicle_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_vehicle(title, make, model, year, price, mileage, fuel_type, transmission, description, image_url, status='available'):
    now = datetime.now().isoformat()
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (title, make, model, year, price, mileage, fuel_type, transmission, description, image_url, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, make, model, year, price, mileage, fuel_type, transmission, description, image_url, status, now))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating vehicle: {e}")
        return None
    finally:
        conn.close()


def delete_vehicle(vehicle_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
        conn.commit()
    finally:
        conn.close()



# ============ CAR COMPARISON ============

def list_car_specs():
    conn = get_db()
    try:
        cursor = conn.cursor()
        # Order alphabetically by make, then model
        cursor.execute('SELECT * FROM car_specs ORDER BY make ASC, model ASC')
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_car_spec(car_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM car_specs WHERE id = ?', (car_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_car_spec(make, model, year, body_type, engine_cc, fuel_type, fuel_efficiency, reliability_score, maintenance_cost, resale_value, spares_availability, notes):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO car_specs (make, model, year, body_type, engine_cc, fuel_type, fuel_efficiency, reliability_score, maintenance_cost, resale_value, spares_availability, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (make, model, year, body_type, engine_cc, fuel_type, fuel_efficiency, reliability_score, maintenance_cost, resale_value, spares_availability, notes))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating car spec: {e}")
        return None
    finally:
        conn.close()

def delete_car_spec(car_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM car_specs WHERE id = ?', (car_id,))
        conn.commit()
    finally:
        conn.close()
