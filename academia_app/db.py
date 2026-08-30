import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "gym.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    c.execute('''
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        price REAL DEFAULT 0
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
        FOREIGN KEY(plan_id) REFERENCES plans(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

# Plans
def add_plan(name, price=0.0):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO plans(name, price) VALUES(?,?)', (name, price))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        c.execute('SELECT id FROM plans WHERE name = ?', (name,))
        row = c.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

def get_plans():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, name, price FROM plans ORDER BY name')
    rows = c.fetchall()
    conn.close()
    return rows

# Clients
def add_client(name, email=None, phone=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO clients(name, email, phone) VALUES(?,?,?)', (name, email, phone))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return cid

def get_clients():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone FROM clients ORDER BY name')
    rows = c.fetchall()
    conn.close()
    return rows

def get_client(client_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone FROM clients WHERE id = ?', (client_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_client(client_id, name, email, phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE clients SET name=?, email=?, phone=? WHERE id=?', (name, email, phone, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM clients WHERE id=?', (client_id,))
    conn.commit()
    conn.close()

# Enrollments
def enroll_client(client_id, plan_id, start_date=None, end_date=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO enrollments(client_id, plan_id, start_date, end_date) VALUES(?,?,?,?)',
              (client_id, plan_id, start_date, end_date))
    conn.commit()
    conn.close()

def get_enrollments():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    SELECT e.id, c.name as client, p.name as plan, e.start_date, e.end_date
    FROM enrollments e
    JOIN clients c ON c.id = e.client_id
    JOIN plans p ON p.id = e.plan_id
    ORDER BY e.start_date DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows
