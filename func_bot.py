import datetime
import logging
import os

import telebot
from dotenv import load_dotenv
from telebot.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, ReplyKeyboardRemove,
                           Update)
from telegram import Update
from telegram.ext import CallbackContext
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
        keyboard = [
            [
                InlineKeyboardButton("Москва", callback_data='1'),
                InlineKeyboardButton("Санкт-Петербург", callback_data='2'),
            ],
            [
                InlineKeyboardButton("Option 3", callback_data='3')],
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(message.chat.id, 'Для какого города?',
                         reply_markup=reply_markup)
        exit()
        bot.send_message(message.chat.id, 'Для какого города?')
        if text != '':
            weather = get_weather(text)
            bot.send_message(message.chat.id,
                             f'Прогноз погоды для {text}: -- {weather}')
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


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call,
        name=name, action=action,
        year=year, month=month,
        day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"You have chosen {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
        )
        print(f"{calendar_1_callback}: Cancellation")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    bot.infinity_polling()
