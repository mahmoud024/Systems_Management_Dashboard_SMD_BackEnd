import sqlite3
from datetime import datetime
import configparser
import os

def create_or_update_db():
    """Create tables and update schema if necessary."""
    conn = sqlite3.connect('smd.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        location TEXT NOT NULL,
        version TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservation (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        server_id INTEGER NOT NULL,
        reservation_from_date TEXT NOT NULL,
        reservation_to_date TEXT NOT NULL,
        is_reserved INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (server_id) REFERENCES servers (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def delete_expired_reservations():
    """Delete reservations that have expired."""
    conn = sqlite3.connect('smd.db')
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute('''
    DELETE FROM reservation 
    WHERE reservation_to_date < ? 
    ''', (now,))
    
    conn.commit()
    conn.close()

# Create or update the database
create_or_update_db()

# Example servers data with file paths included
# Servers data with locations included
servers = [
    ('EX-G9IPC1', '15.17.224.207', 'Rehovot' , ''),
    ('EX-Z8G4TW3', '15.17.224.202', 'Rehovot', ''),
    ('V-DFESRV-IPC05', '15.17.228.101', 'Rehovot', ''),
    ('V-DFESRV-IPC06', '15.17.229.49', 'Rehovot', ''),
    ('IPC-Sim33', '15.17.224.224', 'Rehovot', ''),
    ('IPC-Sim28', '15.17.225.100', 'Rehovot', ''),
    ('EX-G9IPC2', '15.17.224.214', 'Rehovot', ''),
    ('IPC-Sim55', '15.17.224.206', 'Rehovot', ''),
    ('EX-G9TW1', '15.17.225.36', 'Rehovot', ''),
    ('EX-Z8G4-1', '15.17.224.75', 'Rehovot', ''),
    ('EX-Z8G4-3', '15.17.232.60', 'Rehovot', ''),
    ('EX-G9TW2', '15.17.232.71', 'Rehovot', ''),
    ('IPC-Sim54', '15.17.225.18', 'Rehovot', ''),
    ('IPC-Sim23', '15.17.224.62', 'Rehovot', ''),
    ('IPC-Sim30', '15.17.224.149', 'Rehovot', ''),
    ('IPC-Sim6', '15.17.233.153', 'Rehovot', ''),
    ('IPC-Sim35', '15.17.224.221', 'Rehovot', ''),
    ('V-dfesrv-ipc25', '15.17.228.52', 'Rehovot', ''),
    ('V-dfesrv-ipc26', '15.17.228.83', 'Rehovot', ''),
    ('IPC-Sim36', '15.17.224.165', 'Rehovot', ''),
    ('wfc-8000-e', '15.17.224.77', 'Rehovot', ''),
    ('ipc-nightly', '15.17.225.66', 'Rehovot', ''),
    ('ipc-nightly2', '15.17.225.95', 'Rehovot', ''),
    ('EX-Z8G4-4', '15.17.224.63', 'Rehovot', ''),
    ('EX-Z8G4-5', '15.17.224.112', 'Rehovot', ''),
    ('IPC-Ramon2-i3', '15.17.225.132', 'Rehovot', ''),
    ('IPC-SIM51', '15.17.224.78', 'Rehovot', ''),
    ('IPC-Sim72', '15.17.224.248', 'Rehovot', ''),
    ('G8D16-SM4', '15.13.214.108', 'Boise', ''),
    ('G8D16-SM1', '15.13.214.112', 'Boise', ''),
    ('G9B10-SM4', '15.13.212.60', 'Boise', ''),
    ('G9B10-SM7', '15.13.212.73', 'Boise', ''),
    ('G9D7-SM1', '15.13.214.81', 'Boise', ''),
    ('G8B2-SM1', '15.13.214.109', 'Boise', ''),
    ('G8D2-SM2', '15.13.214.113', 'Boise', ''),
    ('G8B2-SM2', '15.13.214.110', 'Boise', '')
]


# Delete existing entries in servers table
conn = sqlite3.connect('smd.db')
cursor = conn.cursor()
cursor.execute('DELETE FROM servers')
conn.commit()
conn.close()

# Insert servers into the database
conn = sqlite3.connect('smd.db')
cursor = conn.cursor()
for name, ip_address, location, file_path in servers:
    cursor.execute('INSERT OR IGNORE INTO servers (name, ip_address, location) VALUES (?, ?, ?)',
                   (name, ip_address, location))

conn.commit()
conn.close()

# Delete expired reservations
delete_expired_reservations()
