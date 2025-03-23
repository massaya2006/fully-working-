from flask import Flask, request, jsonify
import sqlite3
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('arymndb')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role=data.get('role')

    if not email or not password or not role:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Log the received data
    logging.debug(f"Received signup request: Email: {email}, Password: {password}")

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor=conn.cursor()
        
        # Insert the new user into the database
        cursor.execute('INSERT INTO sign (email, password, role) VALUES (?, ?, ?)', (email, password, role))
        conn.commit()
        
        # Close the database connection
        user = cursor.execute('SELECT * FROM sign WHERE email = ?', (email,)).fetchone()
        conn.close()
       
        
        return jsonify({"message": "User registered successfully", "user": dict(user)}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        logging.error(f"Error during signup: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user by email and password
        user = cursor.execute('SELECT * FROM sign WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            return jsonify({"message": "Login successful", "user": dict(user)}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)