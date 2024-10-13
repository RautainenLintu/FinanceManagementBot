import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

class AddAccountStates(StatesGroup):
    AddAccountID = State()

class DeleteAccountStates(StatesGroup):
    DeleteAccountID = State()

class Account:

    def __init__(self, account_id, telegram_id) -> None:
        self.telegram_id = telegram_id
        self.account_id = account_id

    def checkAccountRecord(self):
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id INTEGER PRIMARY KEY, telegram_id INTEGER)''')
        cursor.execute(f'SELECT * FROM accounts WHERE account_id = {self.account_id} AND telegram_id = {self.telegram_id}')
        db_data = cursor.fetchone()
        if db_data is None:
            result = None
            conn.close()
        else:
            result = db_data[0]
            conn.close()
        return result

    def seeAccountRecord(telegram_id):
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id INTEGER PRIMARY KEY, telegram_id INTEGER)''')
        cursor.execute(
            f'SELECT * FROM accounts WHERE telegram_id = {telegram_id}')
        account_list = cursor.fetchall()
        conn.close()
        return account_list

    def createAccountRecord(self):
        insterted_id = None
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id INTEGER PRIMARY KEY)''')
        cursor.execute(f'INSERT INTO accounts (account_id, telegram_id) VALUES ({self.account_id}, {self.telegram_id})')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    def deleteAccountRecord(self):
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id INTEGER PRIMARY KEY, telegram_id INTEGER)''')
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.account_id} AND telegram_id = {self.telegram_id}')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id