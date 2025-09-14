-- Create the database
CREATE DATABASE falcon_finance;

USE falcon_finance;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    dp VARCHAR(255)
);

-- Create transactions table
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date_submitted DATETIME NOT NULL,
    payment_method ENUM('Mobile Money', 'Agent Banking') NOT NULL,
    txn_id VARCHAR(100) NOT NULL,
    receipt VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);