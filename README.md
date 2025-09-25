# About
This is the code meant to accompany the documentation written for my 2025-2026 A-level Computer Science NEA. This README file provides a brief explanation of my NEA for those
who cannot see the full documentation.

# Project information
Mr. G. Maximus of Carpal Inc. has requested an RFID-controlled entry system to be installed into their new server rooms located in Swansea, Wales. These doors should be
accompanied by a monitoring system, which will allow for their security team to identify any unusual activities in or out of the rooms in which this system has been installed.

## Database structure
The monitoring system sends all data from the doors (who enters and when, etc.) to a remote database which will then be viewed and analysed by custom-made software. This
database is made of 3 tables, a *Users* table, a *Department* table, and an *Access Log* table. The *Users* table contains all the employees who have a registered RFID card;
the *Department* table has all the relevant, registered departments with a unique ID, and *Access Log* contains a log of all access attempts through the doors.

## Custom software
The custom software, coded in python, allows the security department to interact and analyse the data through a user-friendly interface. It allows for brief data overviews, 
custom SQL queries, a secure login system, among other useful features.
