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
            /deleteAccount - удаление счета. TODO: удаление всех открытых позиций при удалении аккаунта (автоматическое закрытие позиций)
            /addTransaction - добавление транзакции
            /deleteTransaction - удаление транзакции
            /seePortfolio - TODO
            /totalPortfolio - TODO
            /portfolioStructure - TODO

            Если бот не отвечает на запросы или Вы нашли баг - пожалуйста, сообщите разработчице в телеграм @Rautainen_Lintu
            '''
        return help_msg