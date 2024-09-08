import telebot
import requests

API_TOKEN = '6609928107:AAHnsEJA1yLR9kDdJEMjsxDMRMwKM6OVV4g'
bot = telebot.TeleBot(API_TOKEN)

CURRENCY_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

available_currencies = ["USD", "EUR", "PLN"]


def get_currency_rates():
    response = requests.get(CURRENCY_API_URL)
    data = response.json()
    rates = {item['ccy']: float(item['sale']) for item in data if item['ccy'] in available_currencies}
    return rates


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Я допоможу тобі конвертувати гривні в іноземну валюту. "
                          "Напиши /currencies, щоб побачити доступні валюти для обміну.")


@bot.message_handler(commands=['currencies'])
def list_currencies(message):
    currencies = ', '.join(available_currencies)
    bot.reply_to(message, f"Доступні валюти для обміну: {currencies}. "
                          f"Напиши валюту, в яку ти хочеш обміняти гривні (наприклад, USD).")


@bot.message_handler(func=lambda message: message.text.upper() in available_currencies)
def get_exchange_amount(message):
    currency = message.text.upper()
    msg = bot.reply_to(message, f"Ти вибрав {currency}. Введи суму в гривнях, яку хочеш обміняти.")
    bot.register_next_step_handler(msg, lambda m: convert_currency(m, currency))


def convert_currency(message, currency):
    try:
        uah_amount = float(message.text)
        rates = get_currency_rates()
        if currency in rates:
            converted_amount = uah_amount / rates[currency]
            bot.reply_to(message, f"{uah_amount} грн = {converted_amount:.2f} {currency}")
        else:
            bot.reply_to(message, "Валюта недоступна. Спробуй ще раз.")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введи коректну числову суму.")


bot.polling()
