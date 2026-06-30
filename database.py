import sqlite3
import json

conn = sqlite3.connect("orders.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    phone TEXT,
    province TEXT,
    address TEXT,
    size TEXT,
    quantity TEXT,
    color TEXT,
    price TEXT,
    photos TEXT,
    status TEXT,
    message_id INTEGER
)
""")

conn.commit()


def get_next_code():
    cur.execute("SELECT code FROM orders ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()

    if row:
        num = int(row[0].split("-")[1]) + 1
    else:
        num = 500

    return f"NOA-{num:04d}"


def save_order(data):
    cur.execute("""
    INSERT INTO orders
    (
        code,
        phone,
        province,
        address,
        size,
        quantity,
        color,
        price,
        photos,
        status,
        message_id
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()


def get_order(code):
    cur.execute(
        "SELECT * FROM orders WHERE code=?",
        (code,)
    )
    return cur.fetchone()


def update_status(code, status):
    cur.execute(
        "UPDATE orders SET status=? WHERE code=?",
        (status, code)
    )
    conn.commit()


def update_photos(code, photos):
    cur.execute(
        "UPDATE orders SET photos=? WHERE code=?",
        (json.dumps(photos), code)
    )
    conn.commit()


def update_message_id(code, message_id):
    cur.execute(
        "UPDATE orders SET message_id=? WHERE code=?",
        (message_id, code)
    )
    conn.commit()