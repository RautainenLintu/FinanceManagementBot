from ClassPortfolio import Portfolio
from apimoexIntegration import checkSecurityExistence, getSecurityPrice
from ClassPosition import Position
from ClassUser import User
from ClassAccount import Account, AddAccountStates, DeleteAccountStates, UpdateBalanceStates
from ClassTransaction import Transaction, AddTransactionStates, DeleteTransactionStates, SeeTransactionStates
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from help_msg import HelpMessage
from checkSyntax import checkDate

# bot = Bot(token="BOT_TOKEN")
bot = Bot(token="7354546719:AAGhejY3xBphGd8OmpoZpjSEc1Ni_L5QLTQ")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user = User(message.from_user.id)
    user_record = user.checkUserRecord()
    if user_record is None:
        user.createUserRecord()
        await message.reply("Добро пожаловать в бот! Для вывода списка и описания команд введите /help")
    else:
        await message.reply("С возвращением в бот! Для вывода списка и описания команд введите /help")


@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):
    help_msg = HelpMessage.print_message()
    await message.reply(help_msg)


@dp.message_handler(commands=['addAccount'])
async def addAccount_start(message: types.Message):
    await message.reply("Введите номер счета и сумму на счету в формате НОМЕР_СЧЕТА РУБ.КОП. Например: 133654723897423 2000.00")
    await AddAccountStates.AddAccountID.set()


@dp.message_handler(state=AddAccountStates.AddAccountID)
async def addAccount_exec(message: types.Message, state: FSMContext):
    user_input = message.text.split(" ")
    try:
        account_id = user_input[0]
        assert len(user_input[1].split(".")[1]) == 2
        balance = float(user_input[1])
        assert balance >= 0.0
    except:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        account = Account(account_id, message.from_user.id)
        account_record = account.checkAccountRecord()
        if account_record is None:
            account.createAccountRecord(balance)
            await message.reply("Счет успешно добавлен.")
        else:
            await message.reply("Счет уже существует.")
    finally:
        await state.finish()


@dp.message_handler(commands=['updateBalance'])
async def updateBalance_start(message: types.Message):
    await message.reply("Введите номер счета, сумму и тип операции (ПОПОЛНЕНИЕ или СНЯТИЕ) в формате НОМЕР_СЧЕТА РУБ.КОП ТИП. Например: 133654723897423 2000.00 ПОПОЛНЕНИЕ")
    await UpdateBalanceStates.UpdateBalanceID.set()


@dp.message_handler(state=UpdateBalanceStates.UpdateBalanceID)
async def updateBalance_exec(message: types.Message, state: FSMContext):
    user_input = message.text.split(" ")
    try:
        assert len(user_input) == 3
        account_id = user_input[0]
        assert len(user_input[1].split(".")[1]) == 2 or (len(user_input[1].split(".")[1]) == 1 and user_input[1].split(".")[1] == '0')
        sum = float(user_input[1])
        assert sum > 0.0
        update_type = user_input[2]
        assert update_type in ["ПОПОЛНЕНИЕ", "СНЯТИЕ"]
    except:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        try:
            account = Account(account_id, message.from_user.id)
            assert account.checkAccountRecord() is not None
        except AssertionError:
            await message.reply("Счет не существует. Добавьте счет с помощью команды /addAccount и повторите попытку")
        else:
            new_balance = account.updateBalance(sum, update_type)
            if new_balance is not None:
                await message.reply(f"Операция проведена. Новый баланс счета {account_id}: {new_balance} RUB.")
            else:
                await message.reply(f"Ошибка в выполнении операции. Недостаточно средств для снятия со счета.")
    finally:
        await state.finish()


@dp.message_handler(commands=['deleteAccount'])
async def deleteAccount_start(message: types.Message):
    await message.reply("Внимание! При удалении счета все имеющиеся на нем позиции будут автоматически закрыты по рыночной цене. Если Вы хотите продолжить, введите "
                        "номер счета. Если Вы хотите отменить операцию, введите ОТМЕНА.")
    await DeleteAccountStates.DeleteAccountID.set()


@dp.message_handler(state=DeleteAccountStates.DeleteAccountID)
async def deleteAccount_exec(message: types.Message, state: FSMContext):
    if message.text == "ОТМЕНА":
        await message.reply("Операция отменена")
    else:
        account_id = message.text
        account = Account(int(account_id), message.from_user.id)
        account_record = account.checkAccountRecord()
        if account_record is None:
            await message.reply("Счет не существует.")
        else:
            total = account.deleteAccountRecord()
            if total is not None:
                await message.reply(f"Счет успешно удален. Сумма на счете на момент удаления")
            else:
                await message.reply("Ошибка при удалении счета. Попробуйте позднее.")
    await state.finish()


@dp.message_handler(commands=['seeAccounts'])
async def seeAccounts_start(message: types.Message):
    account_list = Account.seeAccountRecord(message.from_user.id)
    if account_list is None:
        await message.reply("Ваши счета не зарегистрированы. Зарегистрируйте первый счет с помощью команды addAccount")
    else:
        msg = "Список счетов:\n"
        for account in account_list:
            msg += "Cчет " + str(account[0]) + "; баланс " + str(account[2]) + " RUB \n"
        await message.reply(msg)


@dp.message_handler(commands=['addTransaction'])
async def addTransaction_start(message: types.Message):
    await message.reply("Введите транзакцию в формате ТИКЕР РУБ.КОП КОЛИЧЕСТВО СЧЕТ ТИП_ТРАНЗАКЦИИ ГГГГ-ММ-ДД. Допустимые типы транзакций - BUY или SELL\n"
                        "Например: SBER 257.10 5 40817810099910004312 BUY 2024-10-10")
    await AddTransactionStates.AddTransactionID.set()


@dp.message_handler(state=AddTransactionStates.AddTransactionID)
async def addTransaction_exec(message: types.Message, state: FSMContext):
    user_input = message.text.split(" ")
    telegram_id = message.from_user.id
    ticker = user_input[0]
    try:
        assert checkSecurityExistence(ticker)
    except AssertionError:
            await message.reply("Тикер не найден на бирже, либо не удалось получить информацию от биржи. Проверьте правильность ввода тикера или повторите запрос позднее.")
    else:
        try:
            price = float(user_input[1])
            assert price > 0
            quantity = int(user_input[2])
            assert quantity > 0
            account_id = user_input[3]
            transaction_type = user_input[4]
            assert transaction_type in ['BUY', 'SELL']
            date = user_input[5]
            assert checkDate(date)
        except:
            await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
        else:
            account = Account(account_id, telegram_id)
            try:
                assert account.checkAccountRecord() is not None
            except AssertionError:
                await message.reply("Счет не существует. Добавьте счет с помощью команды /addAccount и повторите попытку")
                return 0
            transaction = Transaction(telegram_id, ticker, price, quantity, account_id, transaction_type, date)
            if transaction_type == 'BUY':
                total = quantity * price
                try:
                    assert account.checkFundsSufficiency(total)
                except AssertionError:
                    await message.reply(f"Недостаточно средств для покупки. Проверьте баланс счета с помощью /seeAccounts и пополните счет с помощью /updateBalance")
                else:
                    position_data = Position.checkPositionOpened(telegram_id, account_id, ticker)
                    if position_data is None:
                        position = Position(telegram_id, ticker, quantity, account_id)
                        position.OpenPosition()
                    else:
                        Position.updatePosition(position_data[0], quantity)
                    transaction_id = transaction.createTransactionRecord()
                    await message.reply(f"Транзакция добавлена. Номер транзакции {transaction_id}")
                    account.updateBalance(total, "СНЯТИЕ")
            elif transaction_type == 'SELL':
                total = quantity * price
                position_data = Position.checkPositionOpened(telegram_id, account_id, ticker)
                if position_data is None:
                    await message.reply(f"Не найдена доступная к продаже позиция. Убедитесь, что вы купили позицию и внесли ее в бот. Проверьте данные и повторите попытку")
                else:
                    if quantity == position_data[1]:
                        Position.ClosePosition(position_data[0])
                        account.updateBalance(total, "ПОПОЛНЕНИЕ")
                        transaction_id = transaction.createTransactionRecord()
                        await message.reply(f"Транзакция добавлена. Номер транзакции {transaction_id}")
                    elif quantity > position_data[1]:
                        await message.reply(f"Недостаточное количество актива в открытых позициях. Убедитесь в правильности введения данных")
                    else:
                        Position.updatePosition(position_data[0], -quantity)
                        account.updateBalance(total, "ПОПОЛНЕНИЕ")
                        transaction_id = transaction.createTransactionRecord()
                        await message.reply(f"Транзакция добавлена. Номер транзакции {transaction_id}")
    finally:
        await state.finish()


@dp.message_handler(commands=['deleteTransaction'])
async def deleteTransaction_start(message: types.Message):
    await message.reply("Введите номер транзакции (число без буквенных и специальных символов, и пробелов):")
    await DeleteTransactionStates.DeleteTransactionID.set()


@dp.message_handler(state=DeleteTransactionStates.DeleteTransactionID)
async def deleteTransaction_exec(message: types.Message, state: FSMContext):
    try:
        transaction_id = int(message.text)
    except ValueError:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        transaction = Transaction.getTransactionRecord(message.from_user.id, transaction_id)
        if transaction is not None:
            try:
                assert transaction.revertTransaction()
                Transaction.deleteTransactionRecord(message.from_user.id, transaction_id)
                await message.reply("Транзакция успешно удалена.")
            except AssertionError:
                await message.reply("Ошибка при удалении транзакции. Возможно, Вы уже продали позиции, транзакцию по которым пытаетесь отменить.")
        else:
            await message.reply("Транзакция не найдена или принадлежит другому пользователю. Убедитесь в правильности ввода и повторите команду.")
    finally:
        await state.finish()


@dp.message_handler(commands=['seeTransaction'])
async def seeTransaction_start(message: types.Message):
    await message.reply("Введите номер транзакции (число без буквенных и специальных символов, и пробелов):")
    await SeeTransactionStates.SeeTransactionID.set()


@dp.message_handler(state=SeeTransactionStates.SeeTransactionID)
async def seeTransaction_exec(message: types.Message, state: FSMContext):
    try:
        transaction_id = int(message.text)
    except ValueError:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        transaction = Transaction.getTransactionRecord(message.from_user.id, transaction_id)
        if transaction is not None:
            await message.reply(f"Данные транзакции (тикер, цена, количество, счет, тип, дата): "
                                f"{transaction.ticker} {transaction.price} {transaction.quantity} {transaction.account_id} {transaction.transaction_type} {transaction.date}")
        else:
            await message.reply("Транзакция не найдена или принадлежит другому пользователю. Убедитесь в правильности ввода и повторите команду.")
    finally:
        await state.finish()


@dp.message_handler(commands=['seePortfolio'])
async def seePortfolio_start(message: types.Message):
    telegram_id = message.from_user.id
    Portfolio(telegram_id).generateReport()
    with open(f'./app_reports/report_{telegram_id}.xlsx', 'rb') as f1:
        await bot.send_document(message.chat.id, f1)

@dp.message_handler(commands=['totalPortfolio'])
async def seePortfolio_start(message: types.Message):
    telegram_id = message.from_user.id
    total, isIncomplete = Portfolio(telegram_id).totalPortfolio()
    answer = f"Общая стоимость портфолио: {total} RUB. "
    if isIncomplete:
        answer += "В стоимости не учтены активы, для которых не удалось получить данные Мосбиржи. Для генерации подробного отчета введите /seePortfolio"
    await message.reply(answer)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
