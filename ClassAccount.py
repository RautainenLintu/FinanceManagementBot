import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

class AddAccountStates(StatesGroup):
    AddAccountID = State()

class UpdateBalanceStates(StatesGroup):
    UpdateBalanceID = State()

class DeleteAccountStates(StatesGroup):
    DeleteAccountID = State()
    DeleteAccountConfirmation = State()

class Account:

    def __init__(self, account_id, telegram_id) -> None:
        self.telegram_id = telegram_id
        self.account_id = account_id

    def checkAccountRecord(self):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(f'SELECT * FROM accounts WHERE account_id = \'{self.account_id}\' AND telegram_id = {self.telegram_id}')
        db_data = cursor.fetchone()
        if db_data is None:
            result = None
            conn.close()
        else:
            result = db_data[0]
            conn.close()
        return result

    def checkFundsSufficiency(self, sum):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'SELECT balance FROM accounts WHERE telegram_id = {self.telegram_id} AND account_id = \'{self.account_id}\'')
        balance = cursor.fetchone()[0]
        conn.close()
        if balance >= sum:
            return True
        return False


    def updateBalance(self, sum, update_type="ПОПОЛНЕНИЕ"):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'SELECT balance FROM accounts WHERE telegram_id = {self.telegram_id} AND account_id = \'{self.account_id}\'')
        balance = cursor.fetchone()[0]
        new_balance = None
        if update_type == "СНЯТИЕ":
            if balance >= sum:
                new_balance = balance - sum
                cursor.execute(f'UPDATE accounts SET balance = {new_balance} WHERE telegram_id = {self.telegram_id} AND account_id = \'{self.account_id}\'')
                conn.commit()
        else:
            new_balance = balance + sum
            cursor.execute(f'UPDATE accounts SET balance = {new_balance} WHERE telegram_id = {self.telegram_id} AND account_id = \'{self.account_id}\'')
            conn.commit()
        conn.close()
        return new_balance

    @staticmethod
    def seeAccountRecord(telegram_id):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'SELECT * FROM accounts WHERE telegram_id = {telegram_id}')
        account_list = cursor.fetchall()
        conn.close()
        return account_list

    def createAccountRecord(self, init_balance):
        insterted_id = None
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(f'INSERT INTO accounts (account_id, telegram_id, balance) VALUES (\'{self.account_id}\', {self.telegram_id}, {init_balance})')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    def deleteAccountRecord(self):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(f'DELETE FROM accounts WHERE account_id = \'{self.account_id}\' AND telegram_id = {self.telegram_id}')
        conn.commit()

        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id