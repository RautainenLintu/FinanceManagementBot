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
        /seeTransaction - просмотр ранее добавленной транзакции
        /deleteTransaction - удаление транзакции
        /seePortfolio - TODO
        /totalPortfolio - TODO
        Если бот не отвечает на запросы или Вы нашли баг - пожалуйста, сообщите разработчице в телеграм @Rautainen_Lintu
            '''
        return help_msg


# TODO 1. номера счетов
# 2. удаление счета:
# - автоматическое закрытие позиции по рыночной цене (с подтверждением пользователя)
# - перевод или снятие денег (на выбор пользователя)
# 3. просмотр открытых позиций - генерить xlsx файл с текущими стоимостями
# 4. общая стоимость портфолио - сумма кэша и всех позиций по пользователю