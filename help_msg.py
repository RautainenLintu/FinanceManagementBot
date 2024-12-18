class HelpMessage:

    @staticmethod
    def print_message():
        help_msg = '''
        В боте поддерживаются следующие команды:
        /start - запуск бота
        /help - справка по командам
        /addAccount - добавление счета
        /updateBalance - изменение баланса счета
        /seeAccounts - просмотр списка счетов
        /deleteAccount - удаление счета
        /addTransaction - добавление транзакции
        /seeTransaction - просмотр ранее добавленной транзакции
        /deleteTransaction - удаление транзакции
        /seePortfolio - генерация списка открытых позиций в формате XLSX
        /totalPortfolio - вычисление общей стоимости портфолио
        Если бот не отвечает на запросы или Вы нашли баг - пожалуйста, сообщите разработчице в телеграм @Rautainen_Lintu
            '''
        return help_msg


