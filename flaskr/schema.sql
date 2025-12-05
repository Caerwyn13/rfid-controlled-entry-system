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
    received TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actiontype TEXT NOT NULL,
    is_authorised INTEGER,
    FOREIGN KEY (RFID_key) REFERENCES users(RFID_key)
);

CREATE INDEX idx_accesslog_rfid ON accessLog(RFID_key);


INSERT INTO departments(department_id, department_name) VALUES
(1, 'Administration'),
(2, 'Marketing'),
(3, 'Purchasing'),
(4, 'Human Resources'),
(5, 'Shipping'),
(6, 'IT'),
(7, 'Public Relations'),
(8, 'Sales'),
(9, 'Executive'),
(10, 'Finance'),
(11, 'Accounting'),
(12, 'Treasury'),
(13, 'Shareholder Services'),
(14, 'Manufacturing'),
(15, 'Contracting'),
(16, 'Operational Security'),
(17, 'NOC'),
(18, 'Helpdesk'),
(19, 'Recruiting');

