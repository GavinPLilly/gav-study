import sqlite3
from sqlite3 import Error

def print_err(msg: str):
    print("Error: " + msg)
    print("Exiting")
    exit(1)

def dbprint(text):
    print(text)

def get_db_connection():
    try:
        return sqlite3.connect('/home/gavin/study/db/study.sqlite')
    except Exception as e:
        print(e)
        print_err('Error connecting to database')

def print_hi():
    print('hi')
