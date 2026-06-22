import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

try:
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("Reading setup.sql...")
    with open('setup.sql', 'r') as f:
        sql_commands = f.read().split(';')
        
    for command in sql_commands:
        if command.strip():
            print(f"Executing: {command[:50]}...")
            cursor.execute(command)
            
    conn.commit()
    print("Database initialized successfully.")
    
except Error as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
