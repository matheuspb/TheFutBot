#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from typing import Pattern
import passwords
import messages
import logging
import pymongo
from pymongo import MongoClient

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Estaǵios do Fut
VEMPROFUT, FUTMARCADO = range(2)

# Respostas para o Vem pro Fut
GOING, NOTGOING, FAZERTIMES, CANCELAFUT = range(4)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# client = pymongo.MongoClient("mongodb+srv://futmanager:admin@cluster0.wmvup.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
client = pymongo.MongoClient(passwords.MONGO_CLIENT_URL)
db = client["TheFutDatabase"]
jogadores = db["Jogadores"]
futs = db["Futs"]

def add_jogador(id_jogador, goleiro):
    jogador_existente = jogadores.find_one({"_id": id_jogador})

    if jogador_existente == None:
        jogadores.insert_one({
            "_id": id_jogador,
            "mensalista": False,
            "goleiro": goleiro,
            "rank": 500,
            "partidas": {
                "total": 0,
                "vitorias": 0,
                "empates": 0,
                "derrotas": 0
            },
            "saldo_gols": {
                "gols_feitos": 0,
                "gols_sofridos": 0
            }})
        return True
    else:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"goleiro": goleiro}})
        return False

def init_chamada_fut():
    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut != None:
        return False
    else:
        pymongo_mensalistas = jogadores.find({"mensalista": True})
        mensalistas = []
        for pymongo_mensalista in pymongo_mensalistas:
            print(pymongo_mensalista["_id"])
            mensalistas.append(pymongo_mensalista["_id"])


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def c_linha(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username   
    if add_jogador(id_jogador, False):
        update.message.reply_text(id_jogador + ' cadastrado como jogador linha!')
    else:
        update.message.reply_text(id_jogador + ' atualizado para jogador linha!')


def c_goleiro(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username   
    if add_jogador(id_jogador, True):
        update.message.reply_text(id_jogador + ' cadastrado como goleiro!')
    else:
        update.message.reply_text(id_jogador + ' atualizado para goleiro!')


def c_mensalista(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username
    jogador_existente = jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": True}})
        update.message.reply_text(id_jogador + ' agora é um mensalista!')
    else:
        update.message.reply_text(id_jogador + ' não está cadastrado como jogador. Use /goleiro ou /linha para se cadastrar e depois /mensalista para virar um mensalista.')


def c_diarista(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username
    jogador_existente = jogadores.find_one({"_id": id_jogador})
    
    if jogador_existente != None:
        jogadores.update_one({"_id": id_jogador}, {"$set":{"mensalista": False}})
        update.message.reply_text(id_jogador + ' agora é um diarista!')
    else:
        update.message.reply_text(id_jogador + ' não está cadastrado como jogador. Use /goleiro ou /linha para se cadastrar e já será cadastrado como diarista.')


def c_fut(update: Update, context: CallbackContext) -> None:
    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        pymongo_mensalistas = jogadores.find({"mensalista": True})
        mensalistas = []
        for pymongo_mensalista in pymongo_mensalistas:
            mensalistas.append(pymongo_mensalista["_id"])

        futs.insert_one({
            "_id": "chamada_pro_fut",
            "confirmados": mensalistas
        })

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    confirmados = chamada_fut["confirmados"]

    keyboard = [
        [
            InlineKeyboardButton("✅ Vou", callback_data=str(GOING)),
            InlineKeyboardButton("❌ Não vou", callback_data=str(NOTGOING))
        ],
        [InlineKeyboardButton("⚠️ Cancelar o Fut ⚠️", callback_data=str(CANCELAFUT))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(messages.vem_pro_fut_msg(confirmados), reply_markup=reply_markup)

    return VEMPROFUT


def going(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        print(confirmados)
        update.message.reply_text('Não há nenhum Fut em aberto')
        return ConversationHandler.END

    confirmados = chamada_fut["confirmados"]
    
    id_jogador = "@" + query.from_user.username

    for confirmado in confirmados:
        if confirmado == id_jogador:
            return VEMPROFUT

    confirmados.append(id_jogador)
    print(confirmados)

    futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})

    keyboard = [
        [
            InlineKeyboardButton("✅ Vou", callback_data=str(GOING)),
            InlineKeyboardButton("❌ Não vou", callback_data=str(NOTGOING))
        ],
        [InlineKeyboardButton("Fazer Times", callback_data=str(FAZERTIMES))],
        [InlineKeyboardButton("⚠️ Cancelar o Fut ⚠️", callback_data=str(CANCELAFUT))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=messages.vem_pro_fut_msg(confirmados), reply_markup=reply_markup)

    return VEMPROFUT


def not_going(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        print(confirmados)
        update.message.reply_text('Não há nenhum Fut em aberto')
        return ConversationHandler.END

    confirmados = chamada_fut["confirmados"]
    
    id_jogador = "@" + query.from_user.username

    confirmados.remove(id_jogador)

    futs.update_one({"_id": "chamada_pro_fut"}, {"$set":{"confirmados": confirmados}})

    keyboard = [
        [
            InlineKeyboardButton("✅ Vou", callback_data=str(GOING)),
            InlineKeyboardButton("❌ Não vou", callback_data=str(NOTGOING))
        ],
        [InlineKeyboardButton("Fazer Times", callback_data=str(FAZERTIMES))],
        [InlineKeyboardButton("⚠️ Cancelar o Fut ⚠️", callback_data=str(CANCELAFUT))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=messages.vem_pro_fut_msg(confirmados), reply_markup=reply_markup)

    return VEMPROFUT

def cancela_fut(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    chamada_fut = futs.find_one({"_id": "chamada_pro_fut"})
    if chamada_fut == None:
        update.message.reply_text('Não há nenhum Fut em aberto')
        return ConversationHandler.END

    futs.delete_one({"_id": "chamada_pro_fut"})
    query.edit_message_text(text="O Fut foi cancelado")
    return ConversationHandler.END
   

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():

    # TOKEN = "1009113288:AAFrUSq-UqGcQutLJAgsT6CZX-cREXB9hVk"
    TOKEN = passwords.TELEGRAM_TOKEN

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("linha", c_linha))
    dispatcher.add_handler(CommandHandler("goleiro", c_goleiro))
    dispatcher.add_handler(CommandHandler("mensalista", c_mensalista))
    dispatcher.add_handler(CommandHandler("diarista", c_diarista))

    fut_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('vemprofut', c_fut)],
        states={
            VEMPROFUT: [
                CallbackQueryHandler(going, pattern='^' + str(GOING) + '$'),
                CallbackQueryHandler(not_going, pattern='^' + str(NOTGOING) + '$'),
                CallbackQueryHandler(cancela_fut, pattern='^' + str(CANCELAFUT) + '$')
            ]
            # FUTMARCADO: [
            #     CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
            #     CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
            # ],
        },
        fallbacks=[CommandHandler('vemprofut', c_fut)],
    )
    dispatcher.add_handler(fut_conv_handler)

    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()