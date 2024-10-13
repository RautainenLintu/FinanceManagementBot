import requests
import sys
from ClassUser import User
from ClassAccount import Account, AddAccountStates, DeleteAccountStates
from ClassTransaction import Transaction, AddTransactionStates, DeleteTransactionStates
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
import sqlite3
from datetime import datetime

bot = Bot(token="BOT_TOKEN")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user = User(message.from_user.id)
    user_record = user.checkUserRecord()
    if user_record is None:
        user.createUserRecord()
        await message.reply("Добро пожаловать в бот!")
    else:
        await message.reply("С возвращением в бот!")

@dp.message_handler(commands=['addAccount'])
async def addAccount_start(message: types.Message):
    await message.reply("Введите номер счета:")
    await AddAccountStates.AddAccountID.set()

@dp.message_handler(state=AddAccountStates.AddAccountID)
async def addAccount_exec(message: types.Message, state: FSMContext):
    account_id = int(message.text)
    account = Account(int(account_id), message.from_user.id)
    account_record = account.checkAccountRecord()
    if account_record is None:
        account.createAccountRecord()
        await message.reply("Счет успешно добавлен.")
    else:
        await message.reply("Счет уже существует.")
    await state.finish()

@dp.message_handler(commands=['deleteAccount'])
async def deleteAccount_start(message: types.Message):
    await message.reply("Введите номер счета:")
    await DeleteAccountStates.DeleteAccountID.set()

@dp.message_handler(state=DeleteAccountStates.DeleteAccountID)
async def deleteAccount_exec(message: types.Message, state: FSMContext):
    account_id = int(message.text)
    print(account_id)
    account = Account(int(account_id), message.from_user.id)
    account_record = account.checkAccountRecord()
    if account_record is None:
        await message.reply("Счет не существует.")
    else:
        account.deleteAccountRecord()
        await message.reply("Счет успешно удален.")
    await state.finish()

@dp.message_handler(commands=['seeAccounts'])
async def seeAccounts_start(message: types.Message):
    account_list = Account.seeAccountRecord(message.from_user.id)
    if account_list is None:
        await message.reply("Ваши счета не зарегистрированы. Зарегистрируйте первый счет с помощью команды addAccount")
    else:
        msg = "Список счетов:\n"
        for account in account_list:
            msg += str(account[0]) + "\n"
        print(msg)
        await message.reply(msg)

@dp.message_handler(commands=['addTransaction'])
async def addTransaction_start(message: types.Message):
    await message.reply("Введите транзакцию в формате ТИКЕР РУБ.КОП КОЛИЧЕСТВО СЧЕТ ТИП_ТРАНЗАКЦИИ ГГГГ-ММ-ДД. \n"
                        "Например: SBER 257.10 5 40817810099910004312 BUY 2024-10-10")
    await AddTransactionStates.AddTransactionID.set()

@dp.message_handler(state=AddTransactionStates.AddTransactionID)
async def addAccount_exec(message: types.Message, state: FSMContext):
    user_input = message.text.split(" ")
    print(user_input)
    ticker = user_input[0]
    price = float(user_input[1])
    quantity = int(user_input[2])
    account_id = int(user_input[3])
    transaction_type = user_input[4]
    date = user_input[5]
    transaction = Transaction(ticker, price, quantity, account_id, transaction_type, date)
    transaction.createTransactionRecord()
    await message.reply("Транзакция добавлена")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
