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

from re import match
from typing import Pattern
import futdatabase
import messages
import logging
import pymongo
from pymongo import MongoClient

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Read .env file
from dotenv import load_dotenv
import os


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

PLACARINPUT = range(1)
CONVIDADO_POSICAO, CONVIDADO_RANK, CONVIDADO_FINISH = range(3)
CONVIDADO_DELETE = range(1)
CONVIDADO_GOING = range(1)


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
    
    message = update.message.reply_text(messages.vem_pro_fut_msg(confirmados))
    
    futdatabase.set_vemprofut_message_id(message.message_id)


def c_going(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username

    if (futdatabase.futdatabase.get_jogador_by_id(id_jogador) == None):
        update.message.reply_text("Você não está cadastrado! Use /linha ou /goleiro para se cadastrar primeiro, depois use /going para marcar presença no Fut!")

    confirmados = futdatabase.going_to_fut(id_jogador)

    if confirmados == None:
        update.message.reply_text("Não há nenhum Fut em aberto.")
        return

    message_id = futdatabase.get_vemprofut_message_id()
    context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text=messages.vem_pro_fut_msg(confirmados))


def c_notgoing(update: Update, context: CallbackContext) -> None:
    id_jogador = "@" + update.message.from_user.username

    confirmados = futdatabase.not_going_to_fut(id_jogador)

    if confirmados == None:
        update.message.reply_text("Não há nenhum Fut em aberto.")
        return

    message_id = futdatabase.get_vemprofut_message_id()
    context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text=messages.vem_pro_fut_msg(confirmados))


def c_going_convidado(update: Update, context: CallbackContext) -> None:
    nomes_convidados = futdatabase.get_convidados_nomes()
    reply_keyboard = []
    for nome_convidado in nomes_convidados:
        reply_keyboard.append([nome_convidado])

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    
    update.message.reply_text("Selecione o convidado que você quer confirmar",reply_markup=markup)

    return CONVIDADO_GOING


def r_going_convidado_finish(update: Update, context: CallbackContext) -> int:
    id_jogador = update.message.text
    
    print(f'Convidado indo: {id_jogador}')

    confirmados = futdatabase.going_to_fut(id_jogador)

    if confirmados == None:
        update.message.reply_text("Não há nenhum Fut em aberto.")
        return

    message_id = futdatabase.get_vemprofut_message_id()
    context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text=messages.vem_pro_fut_msg(confirmados))

    update.message.reply_text(f'{futdatabase.convidado_nome} confirmado',reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def c_convidado(update: Update, context: CallbackContext) -> None:
    message = update.message.reply_text("Informe o nome do convidado")
    futdatabase.convidado_message_id = message.message_id
    
    return CONVIDADO_POSICAO

def r_convidado_posicao(update: Update, context: CallbackContext) -> int:
    convidado_nome = update.message.text
    
    if futdatabase.get_jogador_by_id(convidado_nome) != None:
        update.message.reply_text(f"Já existe um jogador com nome {futdatabase.convidado_nome} cadastrado")
        return ConversationHandler.END
    
    futdatabase.convidado_nome = update.message.text
    reply_keyboard = [
        ['Goleiro'],
        ['Linha'],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    
    update.message.reply_text(f"{futdatabase.convidado_nome} joga em que posição?",reply_markup=markup)

    return CONVIDADO_RANK

def r_convidado_rank(update: Update, context: CallbackContext) -> int:
    text_posicao = update.message.text
    if text_posicao == 'Goleiro':
        futdatabase.convidado_goleiro = True
    elif text_posicao == 'Linha':
        futdatabase.convidado_goleiro = False
    else:
        update.message.reply_text('Posição inválida')
        return ConversationHandler.END

    reply_keyboard = [
        ['🥇 Brabo'],
        ['🥈 Ok'],
        ['🥉 Manco'],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(f'Qual é o nível de {futdatabase.convidado_nome} jogando como {text_posicao}?', reply_markup=markup)

    return CONVIDADO_FINISH


def r_convidado_finish(update: Update, context: CallbackContext) -> int:
    text_rank = update.message.text
    if text_rank == '🥇 Brabo':
        futdatabase.convidado_rank = 0.75
    elif text_rank == '🥈 Ok':
        futdatabase.convidado_rank = 0.5
    else:
        futdatabase.convidado_rank = 0.25

    futdatabase.add_convidado()

    update.message.reply_text(f'Adicionado o convidado {futdatabase.convidado_nome}',reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def c_cancela_fut(update: Update, context: CallbackContext) -> None:
    message_id = futdatabase.get_vemprofut_message_id()
    if not futdatabase.cancela_fut():
        update.message.reply_text('Não há nenhum Fut em aberto')
    else:
        context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text='O Fut foi cancelado.')


def c_times(update: Update, context: CallbackContext) -> None:
    times = futdatabase.fazer_times()

    if times == None:
        update.message.reply_text("Não há nenhum Fut em aberto.")
        return

    message_id = futdatabase.get_vemprofut_message_id()
    context.bot.editMessageText(chat_id=update.message.chat_id, message_id=message_id, text=messages.times_msg(times))

def c_placar(update: Update, context: CallbackContext) -> None:
    message = update.message.reply_text(messages.placar_input_msg(futdatabase.home_placar, futdatabase.away_placar, False))
    futdatabase.placar_message_id = message.message_id

    return PLACARINPUT


def r_placar(update: Update, context: CallbackContext) -> int:
    text = int(update.message.text)
    print(f"Placar response: {text}")
    if futdatabase.home_placar == None:
        futdatabase.home_placar = text
        context.bot.editMessageText(chat_id=update.message.chat_id, message_id=futdatabase.placar_message_id, text=messages.placar_input_msg(futdatabase.home_placar, futdatabase.away_placar, False))
        return PLACARINPUT
    else:
        futdatabase.away_placar = text
        
        match_results = {
            "placar":[futdatabase.home_placar, futdatabase.away_placar],
            "times": futdatabase.get_times()
        }

        context.bot.editMessageText(chat_id=update.message.chat_id, message_id=futdatabase.placar_message_id, text=messages.match_results_msg(match_results))
        
        futdatabase.register_match()

        futdatabase.home_placar = None
        futdatabase.away_placar = None
        
        return ConversationHandler.END


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    
    load_dotenv()

    TOKEN = os.getenv('TELEGRAM_TOKEN')

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
    dispatcher.add_handler(CommandHandler("going", c_going))
    dispatcher.add_handler(CommandHandler("notgoing", c_notgoing))
    dispatcher.add_handler(CommandHandler("times", c_times))
    dispatcher.add_handler(CommandHandler("vemprofut", c_fut))
    dispatcher.add_handler(CommandHandler("cancelafut", c_cancela_fut))


    conv_handler_placar = ConversationHandler(
        entry_points=[CommandHandler('placar', c_placar)],
        states={
            PLACARINPUT: [
                MessageHandler(Filters.regex('^[0-9]+$'), r_placar)
            ],
        },
        fallbacks=[MessageHandler(Filters.text, r_placar)],
    )
    dispatcher.add_handler(conv_handler_placar)

    conv_handler_convidado = ConversationHandler(
        entry_points=[CommandHandler('convidado', c_convidado)],
        states={
            CONVIDADO_POSICAO: [
                MessageHandler(Filters.text, r_convidado_posicao)
            ],
            CONVIDADO_RANK: [
                MessageHandler(Filters.text, r_convidado_rank)
            ],
            CONVIDADO_FINISH: [
                MessageHandler(Filters.text, r_convidado_finish)
            ],
        },
        fallbacks=[MessageHandler(Filters.text, r_convidado_posicao)],
    )
    dispatcher.add_handler(conv_handler_convidado)

    conv_handler_convidado_going = ConversationHandler(
        entry_points=[CommandHandler('going_convidado', c_going_convidado)],
        states={
            CONVIDADO_GOING: [
                MessageHandler(Filters.text, r_going_convidado_finish)
            ],
        },
        fallbacks=[MessageHandler(Filters.text, r_going_convidado_finish)],
    )
    dispatcher.add_handler(conv_handler_convidado_going)


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