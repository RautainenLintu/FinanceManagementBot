import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

class BuyPositionStates(StatesGroup):
    BuyPositionID = State()

class SellPositionStates(StatesGroup):
    SellPositionID = State()

class Position:

    def __init__(self, telegram_id, ticker, current_price, quantity, account_id, position_type) -> None:
        self.telegram_id = telegram_id
        self.ticker = ticker
        self.price = current_price
        self.quantity = quantity
        self.account_id = account_id


    @staticmethod
    def OpenPosition(transaction, position_type="LONG"):
        insterted_id = None
        # assert position_type in ['LONG', 'SHORT']
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        # position_type - possible options are LONG and SHORT
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (telegram_id INTEGER, ticker VARCHAR,
                quantity INTEGER, account_id INTEGER, position_type VARCHAR)''')
        cursor.execute(
            f'INSERT INTO positions (telegram_id, ticker, price, quantity, account_id, position_type) VALUES ({transaction.telegram_id}, \'{transaction.ticker}\', '
            f'{transaction.quantity}, {transaction.account_id}, {position_type})')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        return insterted_id

    @staticmethod
    def checkLongPositionOpened(ticker):
        conn = sqlite3.connect('./database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (telegram_id INTEGER, ticker VARCHAR,
                        quantity INTEGER, account_id INTEGER, position_type VARCHAR)''')
        cursor.execute(
            f'INSERT INTO positions (telegram_id, ticker, price, quantity, account_id, position_type) VALUES ({transaction.telegram_id}, \'{transaction.ticker}\', '
            f'{transaction.quantity}, {transaction.account_id}, {position_type})')
        conn.commit()
        insterted_id = cursor.lastrowid
        conn.close()
        pass

    # @staticmethod
    # def checkShortPositionOpened():
    #     pass #TODO

    @staticmethod
    def OpenLongPosition(telegram_id, transaction_id):
        pass

    # @staticmethod
    # def CloseShortPosition(telegram_id, transaction_id):
    #     pass #TODO

    @staticmethod
    def CloseLongPosition(telegram_id, transaction_id):
        pass

    # @staticmethod
    # def checkShortPositionOpened():
    #     pass #TODO