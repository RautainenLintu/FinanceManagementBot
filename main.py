import requests
import sys

from ClassPosition import Position
from ClassUser import User
from ClassAccount import Account, AddAccountStates, DeleteAccountStates, UpdateBalanceStates
from ClassTransaction import Transaction, AddTransactionStates, DeleteTransactionStates
import ClassPosition
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from help_msg import HelpMessage
from aiogram.dispatcher.filters import Command
import sqlite3
from datetime import datetime


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
        account_id = int(user_input[0])
        assert len(user_input[1].split(".")[1]) == 2
        balance = float(user_input[1])
    except:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        account = Account(int(account_id), message.from_user.id)
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
        account_id = int(user_input[0])
        assert len(user_input[1].split(".")[1]) == 2
        sum = float(user_input[1])
        assert sum > 0.0
        assert user_input[2] in ["ПОПОЛНЕНИЕ", "СНЯТИЕ"]
    except:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        account = Account(int(account_id), message.from_user.id)
        account_update = account.updateBalance()
        if account_record is None:
            account.createAccountRecord(balance)
            await message.reply("Счет успешно добавлен.")
        else:
            await message.reply("Счет уже существует.")
    finally:
        await state.finish()

@dp.message_handler(commands=['deleteAccount'])
async def deleteAccount_start(message: types.Message):
    await message.reply("Введите номер счета в числовом формате без буквенных символов, специальных символов и пробелов:")
    await DeleteAccountStates.DeleteAccountID.set()

@dp.message_handler(state=DeleteAccountStates.DeleteAccountID)
async def deleteAccount_exec(message: types.Message, state: FSMContext):
    try:
        account_id = int(message.text)
    except ValueError:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        account = Account(int(account_id), message.from_user.id)
        account_record = account.checkAccountRecord()
        if account_record is None:
            await message.reply("Счет не существует.")
        else:
            account.deleteAccountRecord()
            await message.reply("Счет успешно удален.")
    finally:
        await state.finish()

@dp.message_handler(commands=['seeAccounts'])
async def seeAccounts_start(message: types.Message):
    account_list = Account.seeAccountRecord(message.from_user.id)
    if account_list is None:
        await message.reply("Ваши счета не зарегистрированы. Зарегистрируйте первый счет с помощью команды addAccount")
    else:
        msg = "Список счетов:\n"
        for account in account_list:
            msg += "Cчет " + str(account[0]) + "; баланс " + str(account[2]) + "RUB \n"
        await message.reply(msg)

@dp.message_handler(commands=['addTransaction'])
async def addTransaction_start(message: types.Message):
    await message.reply("Введите транзакцию в формате ТИКЕР РУБ.КОП КОЛИЧЕСТВО СЧЕТ ТИП_ТРАНЗАКЦИИ ГГГГ-ММ-ДД. \n"
                        "Например: SBER 257.10 5 40817810099910004312 BUY 2024-10-10")
    await AddTransactionStates.AddTransactionID.set()

@dp.message_handler(state=AddTransactionStates.AddTransactionID)
async def addTransaction_exec(message: types.Message, state: FSMContext):
    user_input = message.text.split(" ")
    telegram_id = message.from_user.id
    ticker = user_input[0]
    try:
        price = float(user_input[1])
        assert price > 0
        quantity = int(user_input[2])
        assert quantity > 0
        account_id = int(user_input[3])
        transaction_type = user_input[4]
        assert transaction_type in ['BUY', 'SELL']
        date = user_input[5]
    except:
        await message.reply("Некорректный ввод. Пожалуйста, повторите команду.")
    else:
        try:
            assert Account(account_id, telegram_id).checkAccountRecord() is not None
        except AssertionError:
            await message.reply("Счет не существует. Добавьте счет с помощью команды /addAccount и повторите попытку")
            return 0
        transaction = Transaction(telegram_id, ticker, price, quantity, account_id, transaction_type, date)
        if transaction_type == 'BUY':
            pass
        elif transaction_type == 'SELL':
            pass
        else:
            pass
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
        row_number = Transaction.deleteAccountRecord(message.from_user.id, transaction_id)
        if row_number >= 1:
            await message.reply("Транзакция успешно удалена.")
        else:
            await message.reply("Транзакция не найдена или принадлежит другому пользователю. Убедитесь в правильности ввода и повторите команду.")
    finally:
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)