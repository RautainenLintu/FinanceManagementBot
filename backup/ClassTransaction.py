import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup
from ClassAccount import Account
from ClassPosition import Position


class AddTransactionStates(StatesGroup):
    AddTransactionID = State()


class DeleteTransactionStates(StatesGroup):
    DeleteTransactionID = State()


class SeeTransactionStates(StatesGroup):
    SeeTransactionID = State()


class Transaction:

    def __init__(self, telegram_id, ticker, price, quantity, account_id, transaction_type, date) -> None:
        self.telegram_id = telegram_id
        self.ticker = ticker
        self.price = price
        self.quantity = quantity
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.date = date


    def createTransactionRecord(self):
        insterted_id = None
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR, price DOUBLE,
        quantity INTEGER, account_id INTEGER, transaction_type VARCHAR, date DATE)''')
        cursor.execute(f'INSERT INTO transactions (telegram_id, ticker, price, quantity, account_id, transaction_type, date) VALUES ({self.telegram_id}, \'{self.ticker}\', {self.price}, {self.quantity}, {self.account_id}, \'{self.transaction_type}\', \'{self.date}\')')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    @staticmethod
    def getTransactionRecord(telegram_id, transaction_id):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR, price DOUBLE,
                        quantity INTEGER, account_id INTEGER, transaction_type VARCHAR, date DATE)''')
        cursor.execute(f'SELECT * FROM transactions WHERE transaction_id = {transaction_id} AND telegram_id = {telegram_id}')
        conn.commit()
        transaction_data = cursor.fetchone()
        print(transaction_data)
        rowcount = cursor.execute(f'SELECT COUNT(*) FROM transactions WHERE transaction_id = {transaction_id} AND telegram_id = {telegram_id}').fetchone()[0]
        conn.close()
        if rowcount < 1:
            return None
        return Transaction(transaction_data[1], transaction_data[2], transaction_data[3], transaction_data[4], transaction_data[5], transaction_data[6], transaction_data[7])

    @staticmethod
    def deleteTransactionRecord(telegram_id, transaction_id):
        row_number = None
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR, price DOUBLE,
                quantity INTEGER, account_id INTEGER, transaction_type VARCHAR, date DATE)''')
        cursor.execute(f'DELETE FROM transactions WHERE transaction_id = {transaction_id} AND telegram_id = {telegram_id}')
        conn.commit()
        row_number = cursor.rowcount
        conn.close()
        return row_number

    def revertTransaction(self):
        account = Account(self.account_id, self.telegram_id)
        if self.transaction_type == 'SELL':  # revert 'SELL' transaction by "buying" a security
            total = self.quantity * self.price
            position_data = Position.checkPositionOpened(self)
            if position_data is None:
                position = Position(self.telegram_id, self.ticker, self.quantity, self.account_id)
                position.OpenPosition()
            else:
                self.updatePosition(position_data[0], self.quantity)
            transaction_id = self.createTransactionRecord()
            account.updateBalance(total, "СНЯТИЕ")
        else:  # transaction_type == 'BUY'
            total = self.quantity * self.price
            position_data = Position.checkPositionOpened(self)
            if self.quantity == position_data[1]:
                Position.ClosePosition(position_data[0])
                account.updateBalance(total, "ПОПОЛНЕНИЕ")
            else:
                Position.updatePosition(position_data[0], -self.quantity)
                account.updateBalance(total, "ПОПОЛНЕНИЕ")