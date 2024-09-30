import telebot
import requests
from telebot import types

API_TOKEN = 'api_token'
bot = telebot.TeleBot(API_TOKEN)

CURRENCY_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

available_currencies = ["USD", "EUR"]


def get_currency_rates():
    response = requests.get(CURRENCY_API_URL)
    data = response.json()
    rates = {item['ccy']: float(item['sale']) for item in data}

    for currency in available_currencies:
        if currency not in rates:
            rates[currency] = None
    return rates


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Я допоможу тобі конвертувати гривні в іноземну валюту. "
                          "Натисни /currencies, щоб побачити доступні валюти для обміну.")


@bot.message_handler(commands=['currencies'])
def list_currencies(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for currency in available_currencies:
        markup.add(currency)

    bot.send_message(message.chat.id, "Оберіть валюту для обміну:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.upper() in available_currencies)
def get_exchange_amount(message):
    currency = message.text.upper()
    msg = bot.reply_to(message, f"Ти вибрав {currency}. Введи суму в гривнях, яку хочеш обміняти.")
    bot.register_next_step_handler(msg, lambda m: validate_amount(m, currency))


def validate_amount(message, currency):
    try:
        amount_text = message.text.replace(',', '.')
        uah_amount = float(amount_text)
        convert_currency(message, currency, uah_amount)
    except ValueError:
        msg = bot.reply_to(message, "Будь ласка, введи коректну числову суму.")
        bot.register_next_step_handler(msg, lambda m: validate_amount(m, currency))


def convert_currency(message, currency, uah_amount):
    rates = get_currency_rates()
    if currency in rates:
        converted_amount = uah_amount / rates[currency]
        bot.reply_to(message, f"{uah_amount} грн = {converted_amount:.2f} {currency}")
    else:
        bot.reply_to(message, f"Курс для {currency} недоступний зараз. Спробуй пізніше.")


@bot.message_handler(func=lambda message: True)
def handle_unknown_message(message):
    bot.reply_to(message, "Я не розумію це повідомлення. Будь ласка, оберіть валюту для обміну або натисніть /currencies для отримання списку валют.")

bot.polling()
