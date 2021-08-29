import datetime
import logging
import os
import telebot
from dotenv import load_dotenv
from telebot_calendar import RUSSIAN_LANGUAGE, Calendar, CallbackData

from ai_ready import getResponse, intents, model, predict_class
from services.weather import get_weather

load_dotenv()
token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1",
                                   "action",
                                   "year",
                                   "month",
                                   "day")


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('weather', 'calendar', 'talk')
    bot.send_message(message.chat.id, 'Привет', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    text = message.text.lower()
    if text == 'weather':
        bot.send_message(message.chat.id, 'Для какого города?')
        city = input(text)
        if city != '':
            weather = get_weather(city)
            bot.send_message(message.chat.id,
                             f'Прогноз погоды для {city}: -- {weather}')
    elif text == 'calendar':
        now = datetime.datetime.now()
        bot.send_message(
            message.chat.id,
            "Selected date",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,
            ),
        )
    elif text == 'talk':
        ints = predict_class(message.text, model)
        res = getResponse(ints, intents)
        bot.send_message(message.chat.id, res)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    bot.infinity_polling()
