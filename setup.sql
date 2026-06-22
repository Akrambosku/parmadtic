CREATE DATABASE IF NOT EXISTS spaceman_db;
USE spaceman_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    balance DECIMAL(10,2) NOT NULL DEFAULT 1000.00
);

CREATE TABLE IF NOT EXISTS bets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bet_amount DECIMAL(10,2) NOT NULL,
    multiplier DECIMAL(10,2) NOT NULL,
    profit DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert a default test user if it doesn't exist
INSERT IGNORE INTO users (username, balance) VALUES ('testuser', 1000.00);
