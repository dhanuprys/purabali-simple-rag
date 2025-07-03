-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS purabali;

-- Create user and grant permissions
CREATE USER IF NOT EXISTS 'purabali_user'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON purabali.* TO 'purabali_user'@'%';
FLUSH PRIVILEGES;

-- Use the database
USE purabali; 