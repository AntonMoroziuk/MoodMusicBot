import os
import threading

import openai
from telebot import TeleBot

BOT_TOKEN = os.environ.get("BOT_TOKEN")
openai.api_key = os.environ.get("CHAT_GPT_TOKEN")

bot = TeleBot(BOT_TOKEN)
timers = {}


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привіт, я можу підібрати музику під твій настрій. Просто напиши як ти себе почуваєш і я скину тобі кілька треків)",
    )


def set_typing_status(chat_id):
    bot.send_chat_action(chat_id=chat_id, action="typing")
    timer = threading.Timer(4.0, set_typing_status, [chat_id])
    timers[chat_id] = timer
    timer.start()


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat_id = message.chat.id
    set_typing_status(chat_id)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Порадь мені музику під настрій {message.text}."},
    ]
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    timers[chat_id].cancel()
    bot.reply_to(message, reply)


if __name__ == "__main__":
    bot.infinity_polling()
