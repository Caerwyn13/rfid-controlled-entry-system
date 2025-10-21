PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS accessLog;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    RFID_key TEXT UNIQUE,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE accessLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    RFID_key TEXT NOT NULL,
    accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    received CURRENT_TIMESTAMP,
    actiontype TEXT NOT NULL,
    is_authorised INTEGER,
    FOREIGN KEY (RFID_key) REFERENCES users(RFID_key)
);

CREATE INDEX idx_accesslog_rfid ON accessLog(RFID_key);
