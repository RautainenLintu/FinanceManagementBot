import sqlite3
import xlsxwriter
import apimoexIntegration


class Portfolio:
    def __init__(self, telegram_id) -> None:
        self.telegram_id = telegram_id

    def getUserPortfolio(self):
        conn = sqlite3.connect('./app_data/database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS positions (position_id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, ticker VARCHAR,
                        quantity INTEGER, account_id VARCHAR, position_type VARCHAR)''')
        cursor.execute(f'SELECT ticker, account_id, quantity FROM positions WHERE telegram_id = {self.telegram_id}')
        portfolio = cursor.fetchall() # list из элементов tuple, каждый tuple - отдельная позиция
        for i in range(len(portfolio)):
            portfolio[i] = list(portfolio[i])
            price = apimoexIntegration.getSecurityPrice(portfolio[i][0])
            if price is None:
                price = "Ошибка получения цены."
            portfolio[i].append(price)
        conn.close()
        return portfolio


    def totalPortfolio(self):
        portfolio = self.getUserPortfolio()
        total = 0
        isIncomplete = False
        for position in portfolio:
            try:
                quantity = position[2]
                price = float(position[3])
            except:
                isIncomplete = True
            else:
                total += quantity * price
        return total, isIncomplete


    def generateReport(self):
        workbook = xlsxwriter.Workbook(f'./app_data/report_{self.telegram_id}.xlsx')
        worksheet = workbook.add_worksheet()
        portfolio = self.getUserPortfolio()
        row = 0
        col = 0
        headers = ["Тикер", "Счет", "Количество", "Цена"]
        for i in range(4):
            worksheet.write(row, i, headers[i])
        row += 1
        for ticker, quantity, account, price in (portfolio):
            worksheet.write(row, col, ticker)
            worksheet.write(row, col + 1, account)
            worksheet.write(row, col + 2, quantity)
            worksheet.write(row, col + 3, price)
            row += 1
        workbook.close()

