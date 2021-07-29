import os
import random
import json
import pickle
import numpy as np
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters, CallbackContext

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

load_dotenv()
token = os.getenv('TOKEN')

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('dataset.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('telegram_bot.model')


def cleaning_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_words(sentence):
    sentence_words = cleaning_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
        return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_intents = intents_json['intents']
    for i in list_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Hi I am Cee!')


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


print('Starting Bot')

while True:
    message = input("")
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)
