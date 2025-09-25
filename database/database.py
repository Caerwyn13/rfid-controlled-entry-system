import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Database:
    def __init__(self, database, user, password, host, port):
        self.db = database
        self.user = user
        self.pswd = password
        self.host = host
        self.port = port
        self.cursor = self.connect_and_create_cursor()


    def connect_and_create_cursor(self):
        try:
            self.connection = psycopg2.connect(
                database=self.db,
                user=self.user,
                password=self.pswd,
                host=self.host,
                port=self.port
            )
            self.connection.autocommit = True
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except Exception as e:
            print(f"Error {e}")
        return self.connection.cursor()


    def create_database(self, name):
        try:
            self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            print(f"The database {name} has been created sucessfully!!")
        except Exception as e:
            print(f"Error: {e}")

    
    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection closed.")