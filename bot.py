# -*- coding: utf-8 -*-
from telegram import *
from telegram.ext import *
import logging

# Habilitamos el logueo
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level = logging.INFO)
logger = logging.getLogger(__name__)

CHOOSING_CLASS, RESULT, SHOW, NEW_CHOICE = range(4)

# Teclado para elegir la clase
reply_keyboard = [	['Super', 'Lobo'],
					['Monarca', 'Aldeano Entrenado'],
					['Aldeano']  ]

# Teclados para elegir el rol dependiendo de la clase escogida
reply_keyboard_super = [ ['Bruja', 'Asesina'] ]
reply_keyboard_lobo = [ ['Lobo'] ]
reply_keyboard_monarca = [ ['Rey', 'Reina'] ]
reply_keyboard_ald_ent = [  ['Veterano', 'Maldito'],
							['Cazador', 'Martir']  ]
reply_keyboard_aldeano = [ ['Aldeano' , 'Barbero', 'Vidente'],
							['Anciano', 'Anciano Moribundo', 'Cupido'],
							['Ladron', 'Arenero', 'Angel', 'Borracho']]

# Teclado para continuar o terminar
reply_keyboard_continuar = [  ['Continuar', 'Terminar']]


markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard = True)
markup_super = ReplyKeyboardMarkup(reply_keyboard_super, one_time_keyboard = True)
markup_lobo = ReplyKeyboardMarkup(reply_keyboard_lobo, one_time_keyboard = True)
markup_monarca = ReplyKeyboardMarkup(reply_keyboard_monarca, one_time_keyboard = True)
markup_ald_ent = ReplyKeyboardMarkup(reply_keyboard_ald_ent, one_time_keyboard = True)
markup_aldeano = ReplyKeyboardMarkup(reply_keyboard_aldeano, one_time_keyboard = True)
markup_continuar = ReplyKeyboardMarkup(reply_keyboard_continuar, one_time_keyboard = True)


# Eligiendo la clase
def start(bot, update):
	update.message.reply_text(
		"Hola! Mi nombre es CartasLobo."
		"Elige la clase",
		reply_markup = markup)

	return CHOOSING_CLASS

 
# Eligiendo el rol
def choice_rol(bot, update):
	text = update.message.text
	if text == "Super":
		update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = markup_super)
	elif text == "Lobo":
		update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = markup_lobo)
	elif text == "Monarca":
		update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = markup_monarca)
	elif text == "Aldeano Entrenado":
		update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = markup_ald_ent)
	elif text == "Aldeano":
		update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = markup_aldeano)

	return SHOW

# Mostrando el rol elegido
def show_rol(bot, update, user_data):
	text = update.message.text
	user_data['rol'] = text
	update.message.reply_text("El rol elegido es " + text)
	update.message.reply_text("Desea elegir otro rol?", reply_markup = markup_continuar)

	return NEW_CHOICE

# Eligiendo otra clase
def new_class(bot, update):
	update.message.reply_text(
		"Elige otra clase",
		reply_markup = markup)

	return CHOOSING_CLASS


def done(bot, update):
	update.message.reply_text("Nos vemos luego!")
	return ConversationHandler.END


def error(bot, update, error):
	"""Logs errors causados por Updates"""
	logger.warning('La actualizacion "%s" provoco el error "%s"', update, error)


def main():
	updater = Updater("779292309:AAGtRVIL5oS6p5XfuQaCWXr7TsKXP61kXpg")

	# Obtener el despachador para registrar los controladores
	dp = updater.dispatcher

	# Agregue manejador de conversacion con los estados GENDER, PHOTO, LOCATION y BIO
	conv_handler = ConversationHandler(
		entry_points = [CommandHandler('start', start)],

		states = {
			CHOOSING_CLASS:[RegexHandler('^(Super|Lobo|Monarca|Aldeano Entrenado|Aldeano)$',
										choice_rol),
						],

			SHOW: [RegexHandler('^(Bruja|Asesina|Lobo|Rey|Reina|Veterano|Maldito|Cazador|Martir|Aldeano|Barbero|Vidente|Anciano|Anciano Moribundo|Cupido|Ladron|Arenero|Angel|Borracho)$',
				show_rol,
				pass_user_data = True),
				],

			NEW_CHOICE: [RegexHandler('^Continuar$',
										new_class)]

			},

		fallbacks = [RegexHandler('^Terminar$', done)]
	)

	dp.add_handler(conv_handler)

	# Log all errors
	dp.add_error_handler(error)

	# Empieza el bot
	updater.start_polling()

	updater.idle()


if __name__ == '__main__':
	main()






