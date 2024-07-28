from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import re  # Import the re module


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})  # Allow requests from localhost:4200


def connect_db():
    return sqlite3.connect('smd.db')

def delete_expired_reservations():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Use SQLite's datetime function to get current time in UTC
    cursor.execute("SELECT datetime('now')")
    now = cursor.fetchone()[0]
    print(f"Checking for expired reservations at: {now}")

    # Fetch reservations with `reservation_to_date` less than the current time
    cursor.execute('''
    SELECT id, reservation_to_date FROM reservation 
    WHERE datetime(reservation_to_date) < datetime(?)
    ''', (now,))
    expired_reservations = cursor.fetchall()

    print(f"Expired reservations found: {expired_reservations}")

    if expired_reservations:
        # Delete expired reservations
        cursor.execute('''
        DELETE FROM reservation 
        WHERE datetime(reservation_to_date) < datetime(?)
        ''', (now,))
        conn.commit()
        print(f"Deleted expired reservations.")
    else:
        print("No expired reservations to delete.")

    conn.close()

@app.route('/')
def home():
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, avatar FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # For demonstration purposes, use user ID as the token
        token = user[0]  # or generate a real token
        return jsonify({
            "message": "Login successful",
            "token": token,  # Include token in response
            "user": {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "avatar": user[3]
            }
        }), 200
    else:
        return jsonify({"message": "Incorrect email or password"}), 401

# CRUD operations for Servers
@app.route('/servers', methods=['GET'])
def get_servers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servers')
    servers = cursor.fetchall()
    conn.close()
    return jsonify(servers)

@app.route('/servers', methods=['POST'])
def add_server():
    try:
        new_server = request.get_json(force=True)
        name = new_server['name']
        ip_address = new_server['ip_address']
        location = new_server['location']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO servers (name, ip_address, location) VALUES (?, ?, ?)', 
                       (name, ip_address, location))
        conn.commit()
        conn.close()
        return jsonify(new_server), 201
    except Exception as e:
        return str(e), 400

@app.route('/servers/<int:id>', methods=['GET'])
def get_server(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM servers WHERE id = ?', (id,))
    server = cursor.fetchone()
    conn.close()
    return jsonify(server)

@app.route('/servers/<int:id>', methods=['PUT'])
def update_server(id):
    try:
        updated_server = request.get_json()
        if not updated_server:
            return jsonify({"error": "No input data provided"}), 400
        
        name = updated_server.get('name')
        ip_address = updated_server.get('ip_address')
        location = updated_server.get('location')
        
        if not all([name, ip_address, location]):
            return jsonify({"error": "Missing data"}), 400
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE servers 
        SET name = ?, ip_address = ?, location = ? 
        WHERE id = ?''', (name, ip_address, location, id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Server not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": "Server updated successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/servers/<int:id>', methods=['DELETE'])
def delete_server(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        DELETE FROM servers 
        WHERE id = ?''', (id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Server not found"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": "Server deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def extract_product_version(file_path: str) -> str:
    """
    Reads the specified file and extracts the Product version.
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("Product="):
                    # Extract the version number using regex
                    match = re.search(r'Product=(\S+)', line)
                    if match:
                        return match.group(1)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return None

@app.route('/update_product_versions', methods=['GET'])  # Keep as PUT for production
def update_product_versions():
    conn = connect_db()
    cursor = conn.cursor()

    # Retrieve server information from the database
    cursor.execute('SELECT ip_address FROM servers')
    servers = cursor.fetchall()

    for server in servers:
        ip_address = server[0]  # Extract the actual IP address from the tuple

        # Construct the file path
        file_path = f"/Users/mahmoudatia/Desktop/file.txt"

        product_version = extract_product_version(file_path)

        if product_version:
            # Update the version in the database
            cursor.execute('''
                UPDATE servers
                SET version = ?
                WHERE ip_address = ?''', (product_version, ip_address))
            print(f"Updated version for {ip_address} to {product_version}")

        else:
            print(f"No valid Product version found for {ip_address}")

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Product versions updated successfully."}), 200


    
# CRUD operations for Users
@app.route('/users', methods=['GET'])
def get_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'avatar': user[4],
        })
    else:
        return jsonify({'error': 'User not found'}), 404
        
@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.get_json()
    username = new_user['username']
    email = new_user['email']
    password = new_user['password']
    avatar = new_user.get('avatar', '')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, email, password, avatar) VALUES (?, ?, ?, ?)', 
                   (username, email, password, avatar))
    conn.commit()
    conn.close()
    return jsonify(new_user), 201

# CRUD operations for Reservations
@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = connect_db()
    cursor = conn.cursor()

    # Use SQLite's datetime function to get current time in UTC
    cursor.execute("SELECT datetime('now')")
    now = cursor.fetchone()[0]

    # Delete expired reservations
    cursor.execute('''
    DELETE FROM reservation 
    WHERE datetime(reservation_to_date) < datetime(?)
    ''', (now,))
    conn.commit()

    # Fetch the current reservations
    cursor.execute('''
    SELECT r.id, r.user_id, r.server_id, r.reservation_from_date, r.reservation_to_date, u.username, s.name, s.location, r.is_reserved
    FROM reservation r
    JOIN users u ON r.user_id = u.id
    JOIN servers s ON r.server_id = s.id
    WHERE r.is_reserved = 1
    ''')
    reservations = cursor.fetchall()
    conn.close()
    return jsonify(reservations)

@app.route('/reservations', methods=['POST'])
def add_reservation():
    new_reservation = request.get_json()
    user_id = new_reservation['user_id']
    server_id = new_reservation['server_id']
    reservation_from_date = new_reservation['reservation_from_date']
    reservation_to_date = new_reservation['reservation_to_date']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reservation (user_id, server_id, reservation_from_date, reservation_to_date) VALUES (?, ?, ?, ?)', 
                   (user_id, server_id, reservation_from_date, reservation_to_date))
    conn.commit()
    conn.close()
    return jsonify(new_reservation), 201

@app.route('/reservations/<int:id>', methods=['PUT'])
def update_reservation(id):
    updated_reservation = request.get_json()
    user_id = updated_reservation['user_id']
    server_id = updated_reservation['server_id']
    reservation_from_date = updated_reservation['reservation_from_date']
    reservation_to_date = updated_reservation['reservation_to_date']
    is_reserved = updated_reservation.get('is_reserved', 1)
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE reservation 
    SET user_id = ?, server_id = ?, reservation_from_date = ?, reservation_to_date = ?, is_reserved = ?
    WHERE id = ?''', (user_id, server_id, reservation_from_date, reservation_to_date, is_reserved, id))
    conn.commit()
    conn.close()
    return jsonify(updated_reservation)

@app.route('/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reservation WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return '', 204

def read_version_file():
    version_file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'version_info.txt')
    version_info = {}
    if os.path.isfile(version_file_path):
        with open(version_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    version_info[key] = value
    return version_info

@app.route('/version', methods=['GET'])
def get_version():
    version_info = read_version_file()
    return jsonify(version_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)