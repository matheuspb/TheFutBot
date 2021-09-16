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
import futdatabase
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
    if futdatabase.add_jogador(id_jogador, False):
        update.message.reply_text(id_jogador + ' cadastrado como jogador linha!')
    else:
        update.message.reply_text(id_jogador + ' atualizado para jogador linha!')


def c_goleiro(update: Update, context: CallbackContext) -> None:
    
    id_jogador = "@" + update.message.from_user.username   
    
    if futdatabase.add_jogador(id_jogador, True):
        update.message.reply_text(id_jogador + ' cadastrado como goleiro!')
    else:
        update.message.reply_text(id_jogador + ' atualizado para goleiro!')


def c_mensalista(update: Update, context: CallbackContext) -> None:
    
    id_jogador = "@" + update.message.from_user.username
    
    if futdatabase.convert_to_mensalista(id_jogador):
        update.message.reply_text(id_jogador + ' agora é um mensalista!')
    else:
        update.message.reply_text(id_jogador + ' não está cadastrado como jogador. Use /goleiro ou /linha para se cadastrar e depois /mensalista para virar um mensalista.')


def c_diarista(update: Update, context: CallbackContext) -> None:
    
    id_jogador = "@" + update.message.from_user.username
    
    if futdatabase.convert_to_diarista(id_jogador):
        update.message.reply_text(id_jogador + ' agora é um diarista!')
    else:
        update.message.reply_text(id_jogador + ' não está cadastrado como jogador. Use /goleiro ou /linha para se cadastrar e já será cadastrado como diarista.')


def c_fut(update: Update, context: CallbackContext) -> None:
    confirmados = futdatabase.create_fut()

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

    id_jogador = "@" + query.from_user.username

    confirmados = futdatabase.going_to_fut(id_jogador)

    if confirmados == None:
        return ConversationHandler.END

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

    id_jogador = "@" + query.from_user.username

    confirmados = futdatabase.not_going_to_fut(id_jogador)

    if confirmados == None:
        return ConversationHandler.END

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

    if not futdatabase.cancela_fut():
        update.message.reply_text('Não há nenhum Fut em aberto')
    else:
        query.edit_message_text(text="O Fut foi cancelado")
    
    return ConversationHandler.END
   

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
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