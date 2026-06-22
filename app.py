# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app) # Allow frontend to communicate with backend

# Database configuration for Laragon
DB_CONFIG = {
    'host': 'localhost',
    'database': 'spaceman_db',
    'user': 'root', # default laragon username
    'password': ''  # default laragon password
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/api/user', methods=['GET'])
def get_user():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    # Using hardcoded user 'testuser' for now
    cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/api/bet', methods=['POST'])
def place_bet():
    data = request.json
    bet_amount = data.get('bet_amount')
    
    if not bet_amount or bet_amount <= 0:
        return jsonify({"error": "Invalid bet amount"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    # Check balance
    cursor.execute("SELECT id, balance FROM users WHERE username = 'testuser'")
    user = cursor.fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if user['balance'] < bet_amount:
        return jsonify({"error": "Insufficient balance"}), 400
        
    # Deduct balance
    new_balance = float(user['balance']) - float(bet_amount)
    cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, user['id']))
    
    # We create a pending bet record
    cursor.execute(
        "INSERT INTO bets (user_id, bet_amount, multiplier, profit) VALUES (%s, %s, %s, %s)",
        (user['id'], bet_amount, 0.0, 0.0)
    )
    bet_id = cursor.lastrowid
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True, "new_balance": new_balance, "bet_id": bet_id})

@app.route('/api/cashout', methods=['POST'])
def cashout():
    data = request.json
    bet_id = data.get('bet_id')
    multiplier = data.get('multiplier')
    percentage = int(data.get('percentage', 100))
    
    if not bet_id or not multiplier:
        return jsonify({"error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    # Get bet details
    cursor.execute("SELECT * FROM bets WHERE id = %s", (bet_id,))
    bet = cursor.fetchone()
    
    if not bet:
        cursor.close()
        conn.close()
        return jsonify({"error": "Bet not found"}), 404
        
    original_amount = float(bet['bet_amount'])
    
    if percentage == 50:
        cashout_amount = original_amount * 0.5
        remaining_amount = original_amount - cashout_amount
        winnings = cashout_amount * float(multiplier)
        profit_half = winnings - cashout_amount
        
        # Update current bet to represent the cashed out 50%
        cursor.execute(
            "UPDATE bets SET bet_amount = %s, multiplier = %s, profit = %s WHERE id = %s",
            (cashout_amount, multiplier, profit_half, bet_id)
        )
        
        # Insert new bet representing the remaining half
        cursor.execute(
            "INSERT INTO bets (user_id, bet_amount, multiplier, profit) VALUES (%s, %s, %s, %s)",
            (bet['user_id'], remaining_amount, 0.0, 0.0)
        )
        new_bet_id = cursor.lastrowid
        
        # Update user balance
        cursor.execute("SELECT balance FROM users WHERE id = %s", (bet['user_id'],))
        user = cursor.fetchone()
        new_balance = float(user['balance']) + winnings
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, bet['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True, 
            "new_balance": new_balance, 
            "profit": profit_half, 
            "active_bet_id": new_bet_id
        })
    else:
        profit = original_amount * float(multiplier)
        
        # Update bet record
        cursor.execute(
            "UPDATE bets SET multiplier = %s, profit = %s WHERE id = %s",
            (multiplier, profit - original_amount, bet_id)
        )
        
        # Add profit to user balance
        cursor.execute("SELECT balance FROM users WHERE id = %s", (bet['user_id'],))
        user = cursor.fetchone()
        
        new_balance = float(user['balance']) + profit
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, bet['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "new_balance": new_balance, "profit": profit - original_amount})

@app.route('/api/crash', methods=['POST'])
def crash():
    data = request.json
    bet_id = data.get('bet_id')
    
    if not bet_id:
        return jsonify({"error": "Missing parameters"}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cursor = conn.cursor(dictionary=True)
    
    # Update bet record to show 0 multiplier and 0 profit
    cursor.execute(
        "UPDATE bets SET multiplier = %s, profit = %s WHERE id = %s",
        (0.0, -1.0, bet_id) # Using -1 as a marker or just 0
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/history', methods=['GET'])
def history():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cursor = conn.cursor(dictionary=True)
    # Get last 10 completed bets (multiplier > 0 means cashed out)
    cursor.execute("""
        SELECT multiplier FROM bets 
        WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
        AND multiplier > 0
        ORDER BY created_at DESC LIMIT 10
    """)
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
