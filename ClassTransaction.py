import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

class AddTransactionStates(StatesGroup):
    AddTransactionID = State()

class DeleteTransactionStates(StatesGroup):
    DeleteTransactionID = State()

class Transaction:

    def __init__(self, ticker, price, quantity, account_id, transaction_type, date) -> None:
        self.ticker = ticker
        self.price = price
        self.quantity = quantity
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.date = date


    def createTransactionRecord(self):
        insterted_id = None
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, ticker VARCHAR, price DOUBLE, 
        quantity INTEGER, account_id INTEGER, transaction_type VARCHAR, date DATE)''')
        cursor.execute(f'INSERT INTO transactions (ticker, price, quantity, account_id, transaction_type, date) VALUES ({self.ticker}, {self.price}, {self.quantity}, {self.account_id}, {self.transaction_type}, {self.date})')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    # def deleteAccountRecord(self):
    #     conn = sqlite3.connect('./database.db')
    #     cursor = conn.cursor()
    #     cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, ticker VARCHAR, price DOUBLE,
    #             quantity INTEGER, account_id INTEGER, transaction_type VARCHAR, date DATE)''')
    #     # cursor.execute(f'INSERT INTO transactions (ticker, price, quantity, account_id, transaction_type, date) '
    #     #                f'VALUES ({self.ticker}, {self.price}, {self.quantity}, {self.account_id}, {self.transaction_type}, {self.date})')
    #     conn.commit()
    #     insterted_id = cursor.lastrowid
    #     conn.close()
    #     return insterted_id