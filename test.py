import main
import unittest
import sqlite3
from unittest import mock

db_path = './app_data/database.db'


class userTests(unittest.TestCase):
    test_telegram_id = 99999999999999
    test_telegram_id_for_creation = 999999999999991
    test_telegram_id_inexistant = 1111111111111111111

    def setUp(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.test_telegram_id,))
        conn.commit()
        conn.close()

    def testCheckUserExistance(self):
        user = main.User(self.test_telegram_id)
        result = user.checkUserRecord()
        self.assertEqual(result, self.test_telegram_id)

    def testCreateUser(self):
        user = main.User(self.test_telegram_id_for_creation)
        user.createUserRecord()
        result_check = user.checkUserRecord()
        self.assertEqual(result_check, self.test_telegram_id_for_creation)
        user = main.User(self.test_telegram_id_inexistant)
        result_check = user.checkUserRecord()
        self.assertIsNone(result_check)

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id,))
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id_for_creation,))
        conn.commit()
        conn.close()


class accountTests(unittest.TestCase):
    test_telegram_id = 111111111111
    test_account_id = '222222222222'
    test_account_id_for_creation = '333333333333'
    test_account_id_inexistant = '4444444444444'
    test_init_balance = 20000.00

    def setUp(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.test_telegram_id,))
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'INSERT INTO accounts (account_id, telegram_id, balance) VALUES (\'{self.test_account_id}\', '
            f'{self.test_telegram_id}, {self.test_init_balance})')
        conn.commit()
        conn.close()

    def testCheckAccountRecord(self):
        account = main.Account(self.test_account_id, self.test_telegram_id)
        result = account.checkAccountRecord()
        self.assertEqual(result, self.test_account_id)

    def testCreateAccount(self):
        account = main.Account(self.test_account_id_for_creation, self.test_telegram_id)
        account.createAccountRecord(self.test_init_balance)
        result = account.checkAccountRecord()
        self.assertEqual(result, self.test_account_id_for_creation)
        account = main.Account(self.test_account_id_inexistant, self.test_telegram_id)
        result_not = account.checkAccountRecord()
        self.assertIsNone(result_not)

    def testSeeAccountRecord(self):
        result = main.Account.seeAccountRecord(self.test_telegram_id)
        self.assertEqual(result[0][0], self.test_account_id)
        self.assertEqual(result[0][1], self.test_telegram_id)
        self.assertEqual(result[0][2], self.test_init_balance)


    def testCheckFundsSufficiency(self):
        account = main.Account(self.test_account_id, self.test_telegram_id)
        self.assertTrue(account.checkFundsSufficiency(10000.0))
        self.assertTrue(account.checkFundsSufficiency(0.0))
        self.assertFalse(account.checkFundsSufficiency(40000.0))
        self.assertFalse(account.checkFundsSufficiency(20000.01))

    def testUpdateBalance(self):
        account = main.Account(self.test_account_id, self.test_telegram_id)
        self.assertEqual(account.updateBalance(2000.0, "ПОПОЛНЕНИЕ"), 22000.0)
        self.assertEqual(account.updateBalance(2000.0), 24000.0)
        self.assertEqual(account.updateBalance(4000.0, "СНЯТИЕ"), 20000.0)

    def testDeleteAccount(self):
        account = main.Account(self.test_account_id, self.test_telegram_id)
        account.deleteAccountRecord()
        self.assertFalse(account.checkAccountRecord())

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id,))
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.test_account_id} AND telegram_id = {self.test_telegram_id}')
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.test_account_id_for_creation} AND telegram_id = {self.test_telegram_id}')
        conn.commit()
        conn.close()


class positionTests(unittest.TestCase):
    test_telegram_id = 11111111111111
    test_account_id = '222222222222'
    test_init_balance = 20000.00
    test_position1 = main.Position(test_telegram_id, "AFLT", 10, test_account_id, "LONG")
    test_position2 = main.Position(test_telegram_id, "SBER", 10, test_account_id)
    test_position1_id = None

    def setUp(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.test_telegram_id,))
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'INSERT INTO accounts (account_id, telegram_id, balance) VALUES (\'{self.test_account_id}\', '
            f'{self.test_telegram_id}, {self.test_init_balance})')
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                               quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'INSERT INTO positions (telegram_id, ticker, quantity, account_id, position_type) '
                       f'VALUES ({self.test_position1.telegram_id}, \'{self.test_position1.ticker}\', {self.test_position1.quantity}, '
                       f'\'{self.test_position1.account_id}\', \'{self.test_position1.position_type}\')')
        self.test_position1_id = cursor.execute(
            f'SELECT position_id FROM positions WHERE telegram_id = {self.test_position1.telegram_id} AND '
            f'ticker = \'{self.test_position1.ticker}\' AND quantity = {self.test_position1.quantity} AND '
            f'position_type = \'{self.test_position1.position_type}\'').fetchone()[0]
        conn.commit()
        conn.close()


    def testCheckPositionOpened(self):
        self.assertIsNotNone(main.Position.checkPositionOpened(self.test_telegram_id, self.test_account_id, self.test_position1.ticker))
        self.assertIsNone(main.Position.checkPositionOpened(self.test_telegram_id, self.test_account_id, self.test_position2.ticker))

    def testOpenPosition(self):
        row_id = self.test_position2.OpenPosition()
        self.assertGreater(row_id, 0)

    def testUpdatePosition(self):
        main.Position.updatePosition(self.test_position1_id, 20)
        self.assertEqual(main.Position.checkPositionOpened(self.test_position1.telegram_id, self.test_position1.account_id,
                                                           self.test_position1.ticker, self.test_position1.position_type)[1], 30)
        main.Position.updatePosition(self.test_position1_id, -20)
        self.assertEqual(main.Position.checkPositionOpened(self.test_position1.telegram_id, self.test_position1.account_id,
                                              self.test_position1.ticker, self.test_position1.position_type)[1], 10)

    def testClosePosition(self):
        row_id = main.Position.ClosePosition(self.test_position1_id)
        self.assertIsNone(main.Position.checkPositionOpened(self.test_position1.telegram_id, self.test_position1.account_id, self.test_position1.ticker, self.test_position1.position_type))

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id,))
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.test_account_id} AND telegram_id = {self.test_telegram_id}')
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.test_account_id} AND telegram_id = {self.test_telegram_id}')
        cursor.execute(
            f'DELETE FROM positions WHERE telegram_id = {self.test_position1.telegram_id} AND ticker = \'{self.test_position1.ticker}\' AND '
            f'account_id = \'{self.test_position1.account_id}\' AND position_type = \'{self.test_position1.position_type}\'')
        cursor.execute(
            f'DELETE FROM positions WHERE telegram_id = {self.test_position2.telegram_id} AND ticker = \'{self.test_position2.ticker}\' AND '
            f'account_id = \'{self.test_position2.account_id}\' AND position_type = \'{self.test_position2.position_type}\'')
        conn.commit()
        conn.close()

class TransactionTests(unittest.TestCase):
    test_telegram_id = 11111111111111
    test_account_id = '222222222222'
    test_transaction_buy = main.Transaction(test_telegram_id, "SBER", 257.0, 10, test_account_id, "BUY", '2024-10-10')
    test_transaction_sell = main.Transaction(test_telegram_id, "SBER", 257.0, 5, test_account_id,"SELL", '2024-10-10')
    test_position = main.Position(test_telegram_id, "SBER", 5, test_account_id, "LONG")
    test_init_balance = 20000.00
    test_transaction_buy_id = None

    def setUp(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY)')
        cursor.execute('INSERT INTO users (telegram_id) VALUES (?)', (self.test_telegram_id,))
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS accounts (account_id VARCHAR PRIMARY KEY, telegram_id INTEGER, balance DOUBLE)''')
        cursor.execute(
            f'INSERT INTO accounts (account_id, telegram_id, balance) VALUES (\'{self.test_account_id}\', '
            f'{self.test_telegram_id}, {self.test_init_balance})')

        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                               quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'INSERT INTO positions (telegram_id, ticker, quantity, account_id, position_type) '
                       f'VALUES ({self.test_position.telegram_id}, \'{self.test_position.ticker}\', {self.test_position.quantity}, '
                       f'\'{self.test_position.account_id}\', \'{self.test_position.position_type}\')')

        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR, price DOUBLE,
                quantity INTEGER, account_id VARCHAR, transaction_type VARCHAR, date DATE)''')
        cursor.execute(
            f'INSERT INTO transactions (telegram_id, ticker, price, quantity, account_id, transaction_type, date) VALUES ({self.test_transaction_buy.telegram_id}, '
            f'\'{self.test_transaction_buy.ticker}\', {self.test_transaction_buy.price}, {self.test_transaction_buy.quantity}, '
            f'\'{self.test_transaction_buy.account_id}\', \'{self.test_transaction_buy.transaction_type}\', \'{self.test_transaction_buy.date}\')')
        self.test_transaction_buy_id = cursor.execute(f'SELECT transaction_id FROM transactions WHERE telegram_id = {self.test_transaction_buy.telegram_id} AND '
                                                      f'ticker = \'{self.test_transaction_buy.ticker}\' AND price = {self.test_transaction_buy.price} '
                                                      f'AND quantity = {self.test_transaction_buy.quantity} AND account_id = \'{self.test_transaction_buy.account_id}\' '
                                                      f'AND transaction_type = \'{self.test_transaction_buy.transaction_type}\' AND date = \'{self.test_transaction_buy.date}\'').fetchone()[0]
        conn.commit()
        conn.close()

    def testCreateTransactionRecord(self):
        transaction = main.Transaction(self.test_transaction_sell.telegram_id, self.test_transaction_sell.ticker, self.test_transaction_sell.price,
                                       self.test_transaction_sell.quantity, self.test_transaction_sell.account_id, self.test_transaction_sell.transaction_type,
                                       self.test_transaction_sell.date)
        row_id = transaction.createTransactionRecord()
        self.assertGreater(row_id, 0)

    def testGetTransactionRecord(self):
        result_transaction = main.Transaction.getTransactionRecord(self.test_telegram_id, self.test_transaction_buy_id)
        self.assertEqual(result_transaction.telegram_id, self.test_transaction_buy.telegram_id)
        self.assertEqual(result_transaction.ticker, self.test_transaction_buy.ticker)
        self.assertEqual(result_transaction.price, self.test_transaction_buy.price)
        self.assertEqual(result_transaction.quantity, self.test_transaction_buy.quantity)
        self.assertEqual(result_transaction.account_id, self.test_transaction_buy.account_id)
        self.assertEqual(result_transaction.transaction_type, self.test_transaction_buy.transaction_type)
        self.assertEqual(result_transaction.date, self.test_transaction_buy.date)

    def testDeleteTransactionRecord(self):
        row_id = main.Transaction.deleteTransactionRecord(self.test_telegram_id, self.test_transaction_buy_id)
        self.assertGreater(row_id, 0)
        row_id = main.Transaction.deleteTransactionRecord(self.test_telegram_id, self.test_transaction_buy_id)
        self.assertLessEqual(row_id, 0) # transaction is already deleted

    def testRevertTransaction(self):
        # нельзя отменить транзакцию BUY, если нет открытой позиции (транзакция не внесена пользователем)
        test_transaction_buy_revert = main.Transaction(self.test_telegram_id, "AFLT", 200.0, 100, self.test_account_id, "BUY", '2024-10-10')

        # можно отменить транзакцию BUY, только если количество актива в открытой позиции больше или равно количеству актива в отменяемой транзакции
        self.assertFalse(test_transaction_buy_revert.revertTransaction())
        main.Position(self.test_telegram_id, "AFLT", 200, self.test_account_id, "LONG").OpenPosition()
        self.assertTrue(test_transaction_buy_revert.revertTransaction()) # отменяем половину покупки
        self.assertTrue(test_transaction_buy_revert.revertTransaction()) # отменяем вторую половину покупки
        self.assertFalse(test_transaction_buy_revert.revertTransaction()) # отменить покупку еще 100 акций не получится - позиция уже была закрыта другой транзакцией

        # можно отменить транзакцию SELL, только если на счету недостаточно средств (средства от продажи не были уже потрачены в другой транзакции)
        test_transaction_sell_revert = main.Transaction(self.test_telegram_id, "GAZP", 200.0, 150, self.test_account_id,
                                                       "SELL", '2024-10-10')
        self.assertTrue(test_transaction_sell_revert.revertTransaction()) # отменяем половину продажи
        self.assertTrue(test_transaction_sell_revert.revertTransaction()) # отменяем вторую половину продажи
        self.assertFalse(test_transaction_sell_revert.revertTransaction())  # отменить продажу еще 150 акций не получится - недостаточно средств

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE telegram_id = ?', (self.test_telegram_id,))
        cursor.execute(f'DELETE FROM accounts WHERE account_id = {self.test_account_id} AND telegram_id = {self.test_telegram_id}')
        cursor.execute(
            f'DELETE FROM transactions WHERE telegram_id = {self.test_transaction_buy.telegram_id} AND '
            f'ticker = \'{self.test_transaction_buy.ticker}\' AND price = {self.test_transaction_buy.price} '
            f'AND quantity = {self.test_transaction_buy.quantity} AND account_id = \'{self.test_transaction_buy.account_id}\' '
            f'AND transaction_type = \'{self.test_transaction_buy.transaction_type}\' AND date = \'{self.test_transaction_buy.date}\'')
        cursor.execute(f'DELETE FROM positions WHERE telegram_id = {self.test_position.telegram_id} AND ticker = \'{self.test_position.ticker}\' AND '
                       f'account_id = \'{self.test_position.account_id}\' AND position_type = \'{self.test_position.position_type}\'')
        cursor.execute(
            f'DELETE FROM transactions WHERE telegram_id = {self.test_transaction_sell.telegram_id} AND '
            f'ticker = \'{self.test_transaction_sell.ticker}\' AND price = {self.test_transaction_sell.price} '
            f'AND quantity = {self.test_transaction_sell.quantity} AND account_id = \'{self.test_transaction_sell.account_id}\' '
            f'AND transaction_type = \'{self.test_transaction_sell.transaction_type}\' AND date = \'{self.test_transaction_sell.date}\'')
        conn.commit()
        conn.close()


class portfolioTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()

