import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

class BuyPositionStates(StatesGroup):
    BuyPositionID = State()

class SellPositionStates(StatesGroup):
    SellPositionID = State()

class Position:

    def __init__(self, telegram_id, ticker, quantity, account_id, position_type="LONG") -> None:
        self.telegram_id = telegram_id
        self.ticker = ticker
        self.quantity = quantity
        self.account_id = account_id
        self.position_type = position_type


    def OpenPosition(self):
        insterted_id = None
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                               quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'INSERT INTO positions (telegram_id, ticker, quantity, account_id, position_type) '
                       f'VALUES ({self.telegram_id}, \'{self.ticker}\', {self.quantity}, \'{self.account_id}\', \'{self.position_type}\')')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    @staticmethod
    def ClosePosition(position_id):
        insterted_id = None
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                               quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'DELETE FROM positions WHERE position_id = {position_id}')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    @staticmethod
    def checkPositionOpened(telegram_id, account_id, ticker, position_type="LONG"):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                        quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'SELECT position_id, quantity FROM positions WHERE telegram_id = {telegram_id} AND account_id = \'{account_id}\' '
                       f'AND ticker = \'{ticker}\'')
        position_data = cursor.fetchone()
        conn.close()
        return position_data

    @staticmethod
    def updatePosition(position_id, additional_quantity):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                                quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        current_quantity = cursor.execute(f'SELECT quantity FROM positions WHERE position_id = {position_id}')
        total_quantity = current_quantity.fetchone()[0] + additional_quantity
        cursor.execute(f'UPDATE positions SET quantity = {total_quantity} WHERE position_id = {position_id}')
        conn.commit()
        conn.close()

