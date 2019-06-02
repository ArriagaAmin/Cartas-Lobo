# -*- coding: utf-8 -*-
from telegram import *
from telegram.ext import *
import logging
import openpyxl
import random

# Habilitamos el logueo
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level = logging.INFO)
logger = logging.getLogger(__name__)

CHOOSING_CLASS, RESULT, SHOW, NEW_CHOICE = range(4)

# Leemos el archivo Excel
doc = openpyxl.load_workbook('Tabla de Cartas Lobo.xlsx')
tabla = doc['Tabla']
lore = doc['Lore']


################# LAS SIGUIENTES CONSTANTES DEBEN CAMBIARSE SI SE MODIFICA EL ARCHIVO EXCEL ##########################	
# Teclado para elegir la clase
reply_keyboard = [	['Super', 'Lobo'],
					['Monarca', 'Aldeano'],
					['Aldeano Entrenado']  ]
# Teclados para elegir el rol dependiendo de la clase escogida
reply_keyboard_super = [ ['Bruja'] ]
reply_keyboard_lobo = [ ['Lobo'] ]
reply_keyboard_monarca = [ ['Rey', 'Reina'] ]
reply_keyboard_ald_ent = [  ['Veterano', 'Maldito'],
							['Cazador', 'Martir']  ]
reply_keyboard_aldeano = [ ['Aldeano' , 'Barbero', 'Vidente'],
							['Anciano', 'Anciano Moribundo', 'Cupido'],
							['Ladron', 'Arenero', 'Angel', 'Borracho']]
# Teclado para continuar o terminar
reply_keyboard_continuar = [  ['Continuar', 'Terminar']]

# Activamos los teclados anteriores
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard = True)
markup_super = ReplyKeyboardMarkup(reply_keyboard_super, one_time_keyboard = True)
markup_lobo = ReplyKeyboardMarkup(reply_keyboard_lobo, one_time_keyboard = True)
markup_monarca = ReplyKeyboardMarkup(reply_keyboard_monarca, one_time_keyboard = True)
markup_ald_ent = ReplyKeyboardMarkup(reply_keyboard_ald_ent, one_time_keyboard = True)
markup_aldeano = ReplyKeyboardMarkup(reply_keyboard_aldeano, one_time_keyboard = True)
markup_continuar = ReplyKeyboardMarkup(reply_keyboard_continuar, one_time_keyboard = True)

# Variable global que indica si se acabo el tiempo
timeOut = False

# Roles exitentes:
roles = []
for k in range(3, 20):
	roles.append(tabla['B' + str(k)].value)

# Letras donde en el Excel hay roles
letras = "CDEFGHIJKLMNOPQRST"

# Clases existentes y sus teclados correspondientes:
clases_markup = [    ["Super", markup_super], ["Lobo", markup_lobo], ["Monarca", markup_monarca], ["Aldeano Entrenado", markup_ald_ent] , ["Aldeano", markup_aldeano]     ]
clases = [ "Super", "Lobo", "Monarca", "Aldeano Entrenado", "Aldeano" ]

# Roles iniciales de los Jugadores. El numero representa la cantidad
rolesIni = [   ["Bruja", 1], ["Lobo", 3], ["Rey", 1], ["Reina", 1], ["Veterano", 1], ["Maldito", 1], ["Cazador", 2], ["Martir", 1], ["Aldeano", 4], ["Barbero", 1], ["Vidente", 1], ["Anciano", 1], ["Anciano Moribundo", 0], ["Cupido", 1], ["Ladron", 1], ["Arenero", 1], ["Angel", 1], ["Borracho", 1]    ]

# En esta variable global se guardaran los roles del bot
botRoles = []
for k in rolesIni:
	botRoles.append(k)



########################### FUNCIONES CORRESPONDIENTES A UN ESTADO DEL JUEGO ############################### 
def choice_rol(bot, update, job_queue, user_data, chat_data):
	"""En este estado el Jugador ya eligio la Clase y ahora debe elegir el rl correspondiente"""
	global timeOut

	# Eliminamos el temporizador viejo del Jugador
	delTimer(bot, update, user_data)

	# Guardamos el mensaje que envio el Jugador
	text = update.message.text

	# Si no se ha acabado el tiempo y el mensaje del jugado es de una clase, seguimos normalmente
	if (not timeOut) and (text != "Restart"):

		user_data['clase'] = text

		for clase in clases_markup:
			if text == clase[0]:
				update.message.reply_text("Ahora elige el rol de la clase " + text, reply_markup = clase[1])

		setTimer(bot, update, job_queue, user_data, chat_data)

		return SHOW

	# Si no se ha acabado el tiempo y el mensaje es Restart, o se ha acabado el tiempo y el mensaje no es Restart, regresamos a este estado
	elif ((not timeOut) and (text == "Restart")) or (timeOut and (text != "Restart")):
		return CHOOSING_CLASS

	# Si se acabo el tiempo y el mensaje es Restart, reiniciamos el juego
	elif timeOut and text == "Restart":
		timeOut = False
		return start(bot, update, job_queue, user_data, chat_data)

def show_rol(bot, update, job_queue, user_data, chat_data):
	"""El bot elige un rol aleatorio de los que tiene y verifica el resultado del enfrentamiento"""
	global timeOut
	global botRoles

	# Guardamos el mensaje que envio el Jugador
	text = update.message.text

	# Verificamos la clase elegida anteriormente por el usuario
	clase = user_data['clase']

	# Si no se ha acabado el tiempo y el mensaje del jugado es de una clase, seguimos normalmente
	if (not timeOut) and (text != "Restart"):

		# Verificamos que el rol y la clase elegida se corresponden    			# CAMBIAR ESTO SI CAMBIAN EL EXCEL
		if (clase == "Super" and text == "Bruja") or\
			(clase == "Lobo" and text == "Lobo") or\
			(clase == "Monarca" and (text == "Rey" or text == "Reina")) or\
			(clase == "Aldeano Entrenado" and (text == "Veterano" or text == "Maldito" or text == "Cazador" or text == "Martir")) or\
			(clase == "Aldeano" and (text == "Aldeano" or text == "Anciano" or text == "Anciano Moribundo" or text == "Barberp" or text == "Vidente" or text == "Cupido" or text == "Ladron" or text == "Arenero" or text == "Angel" or text == "Borracho")):

				for rol in user_data['roles']:
					# Si aun quedan cartas del rol elegido
					if (rol[0] == text) and (rol[1] != 0):

						# Eliminamos el temporizador viejo del Jugador
						delTimer(bot, update, user_data)

						# El bot elige un rol aleatorio de los que el tiene
						hay = False
						while not hay:
							rdmRol = random.choice(botRoles)
							if rdmRol[1] != 0:
								hay = True

						# Obtenemos la letra del excel correspondiente al rol del bot
						char = charRol(rdmRol[0])
						# Obtenemos el numero del excel correspondiente al rol del Jugador
						number = numberRol(text)
						# El resultado del enfrentamiento de ambos roles es
						resultado = tabla[char + number].value

						update.message.reply_text("El rol que yo escogi es: " + rdmRol[0])

						# Se determina el efecto del enfrentamiento
						win = effect(bot, update, user_data, text, rdmRol, resultado)

						# Verificamos si a alguno de los Jugadores se le acabarn los roles
						if all(rol[1] == 0 for rol in botRoles) or (win == 1):
							return done(bot, update, True)
						elif all(rol[1] == 0 for rol in user_data['roles']) or (win == -1):
							return done(bot, update, False)

						# Si no es asi, repetimos el proceso
						setTimer(bot, update, job_queue, user_data, chat_data)

						update.message.reply_text(
							"Elige otra clase.",
							reply_markup = markup)

						return CHOOSING_CLASS

					elif (rol[0] == text) and (rol[1] == 0):
						update.message.reply_text("No le quedan cartas del rol elegido. Elige otro rol.")

						return SHOW

		# Si no corresponden, regresamos a esta funcion
		else:
			return SHOW


	# Si no se ha acabado el tiempo y el mensaje es Restart, o se ha acabado el tiempo y el mensaje no es Restart, regresamos a este estado
	elif ((not timeOut) and (text == "Restart")) or (timeOut and (text != "Restart")):
		return SHOW

	# Si se acabo el tiempo y el mensaje es Restart, reiniciamos el juego
	elif timeOut and text == "Restart":
		timeOut = False
		return start(bot, update, job_queue, user_data)


	user_data['rol'] = text
	update.message.reply_text("El rol elegido es " + text)
	update.message.reply_text("Desea elegir otro rol?", reply_markup = markup_continuar)

	return NEW_CHOICE

def done(bot, update, win):
	if win:
		update.message.reply_text("Felicidades! Ha ganado el juego.")
	else:
		update.message.reply_text("Ha perdido el juego. Mas suerte para la proxima.")

	update.message.reply_text("Nos vemos luego!")
	return ConversationHandler.END

#################################################### COMANDOS ################################################
def start(bot, update, job_queue, user_data, chat_data):
	"""Inicia el bot."""
	global timeOut
	global botRoles

	timeOut = False

	# Tanto el jugador como el bot tendran las mismas cartas        	# CAMBIAR ESTO SI CAMBIAN EL EXCEL
	user_data['roles'] = [   ["Bruja", 1], ["Lobo", 3], ["Rey", 1], ["Reina", 1], ["Veterano", 1], ["Maldito", 1], ["Cazador", 2], ["Martir", 1], ["Aldeano", 4], ["Barbero", 1], ["Vidente", 1], ["Anciano", 1], ["Anciano Moribundo", 0], ["Cupido", 1], ["Ladron", 1], ["Arenero", 1], ["Angel", 1], ["Borracho", 1]    ]

	botRoles = [   ["Bruja", 1], ["Lobo", 3], ["Rey", 1], ["Reina", 1], ["Veterano", 1], ["Maldito", 1], ["Cazador", 2], ["Martir", 1], ["Aldeano", 4], ["Barbero", 1], ["Vidente", 1], ["Anciano", 1], ["Anciano Moribundo", 0], ["Cupido", 1], ["Ladron", 1], ["Arenero", 1], ["Angel", 1], ["Borracho", 1]    ]

	update.message.reply_text(
		"Bienvenido a la Aldea Mackienze!. Elige la clase del rol que desea jugar:",
		reply_markup = markup)

	setTimer(bot, update, job_queue, user_data, chat_data)

	return CHOOSING_CLASS

def info(bot, update, args, chat_data):
	"""Da la informacion de los lores de los roles."""

	existe = False

	for k in range(2, 20):
		if args[0] == lore['B' + str(k)].value:
			update.message.reply_text(lore['C' + str(k)].value)
			existe = True

	if not existe:
		update.message.reply_text("El rol indicado no existe.")

def misRoles(bot, update, user_data):
	"""Muestra los roles que le quedan al Jugador"""

	update.message.reply_text("Los roles que le quedan son: \n")

	string = ""
	for rol in user_data['roles']:
		string += rol[0] + " (" + str(rol[1]) + ")\n"
	
	update.message.reply_text(string)

def bot_roles(bot, update):
	"""Muestra los roles que le quedan al Bot"""
	global botRoles

	update.message.reply_text("Los roles que me quedan son: \n")

	string = ""
	for rol in botRoles:
		string += rol[0] + " (" + str(rol[1]) + ")\n"
	
	update.message.reply_text(string)


########################################### OTRAS FUNCIONES ####################################################
def error(bot, update, error):
	"""Logs errors causados por Updates"""
	logger.warning('La actualizacion "%s" provoco el error "%s"', update, error)

def convert(arreglo):
	"""Toma un arreglo y une sus elementos en un solo string separados pr |"""

	string = arreglo[0]

	for k in range(2, len(arreglo)):
		string += "|" + arreglo[k]

	return string

def warning(bot, job):
	"""Advertimos al Jugador que se le esta acabando el tiempo"""
	bot.send_message(job.context, text = 'Le quedan 30 segundos para elegir.')

def time_out(bot, job):
	"""Le indicamos al Jugador que se le acabo el tiempo"""
	global timeOut
	timeOut = True

	bot.send_message(job.context, text = 'Se le ha acabado el tiempo, y en consecuencia ha perdido la partida. Escribar "Restart" para reiniciar el juego.')

def setTimer(bot, update, job_queue, user_data, chat_data):
	"""Colocamos al usuario un temporizador"""
	chat_id = update.message.chat_id

	job1 = job_queue.run_once(warning, 30, context = chat_id)
	job2 = job_queue.run_once(time_out, 60, context = chat_id)
	user_data['job1'] = job1
	user_data['job2'] = job2

def delTimer(bot, update, user_data):
	"""Eliminamos los temporizadores del usuario"""

	try:
		job1 = user_data['job1']
		job1.schedule_removal()
		del user_data['job1']

		job2 = user_data['job2']
		job2.schedule_removal()
		del user_data['job2']
	except: 
		pass

def numberRol(rol):
	"""Obtenemos el numero correspondiente a la fikla del excel donde se encuentra el rol indicado"""

	for k in range(3, 21):
		if tabla['B' + str(k)].value == rol:
			return str(k)

def charRol(rol):
	"""Obtenemos el numero correspondiente a la fikla del excel donde se encuentra el rol indicado"""

	for k in range(0, len(letras)):
		if tabla[letras[k] + str(2)].value == rol:
			return letras[k]

def effect(bot, update, user_data, rol1, rol2, resultado):
	"""Determina los efectos del enfrentamiento de dos roles"""

	#################### REVISAR ESTO MINUCIOSAMENTE SI SE CAMBIA EL EXCEL ########################3
	global botRoles

	if resultado == "WIN":
		update.message.reply_text("Un MONARCA ha linchado al Veterano.")
		return 1

	elif resultado == "GANA":
		update.message.reply_text("Ha ganado la batalla!")
		for rol in botRoles:
			if rol[0] == rol2[0]:
				rol[1] -= 1

		# Verificamos los efectos secundarios del rol que gano
		if rol1 == "Bruja":
			user_data['roles'][0][1] -= 1
		elif (rol1 == "Rey" or rol1 == "Reina") and (rol2 == "Anciano" or rol2 == "Anciano Moribundo"):
			num = 0
			for k in range(4, len(rolesIni)):				# CAMBIAR ESTO SI CAMBIAN EL EXCEL
				num += user_data['roles'][k][1]
				user_data['roles'][k][1] = 0

			user_data

	elif resultado == "EMPATA+":
		update.message.reply_text("Ningun rol ha muerto!")

	elif resultado == "EMPATA-":
		update.message.reply_text("Ambos roles han muerto!")
		for rol in botRoles:
			if rol[0] == rol2[0]:
				rol[1] -= 1
		for rol in user_data['roles']:
			if rol[0] == rol1:
				rol[1] -= 1

	elif resultado == "PIERDE":
		update.message.reply_text("Has perdido. Mas suerte a la proxima.")
		for rol in user_data['roles']:
			if rol[0] == rol1:
				rol[1] -= 1

	elif resultado == "LOSE":
		update.message.reply_text("Un MONARCA ha linchado al Veterano.")
		return -1

	return 0


########################################### FUNCION MAIN ####################################################
def main():
	updater = Updater("779292309:AAGtRVIL5oS6p5XfuQaCWXr7TsKXP61kXpg")

	# Obtener el despachador para registrar los controladores
	dp = updater.dispatcher

	# Agregue manejador de conversacion con los estados GENDER, PHOTO, LOCATION y BIO
	conv_handler = ConversationHandler(
		entry_points = [CommandHandler('start', 
										start,
										pass_user_data = True,
										pass_job_queue = True,
										pass_chat_data = True,)
		],

		states = {
			CHOOSING_CLASS:[RegexHandler('^(' + convert(clases) + '|Restart)$',
										choice_rol,
										pass_user_data = True,
										pass_job_queue = True,
										pass_chat_data = True,),
			],

			SHOW: [RegexHandler('^(' + convert(roles) + '|Restart)$',
				show_rol,
				pass_user_data = True,
				pass_job_queue = True,
				pass_chat_data = True,),
			],
		},

		fallbacks = []
	)

	dp.add_handler(conv_handler)
	dp.add_handler(CommandHandler("info", info, pass_args = True, pass_chat_data = True))
	dp.add_handler(CommandHandler("misRoles", misRoles, pass_user_data = True))
	dp.add_handler(CommandHandler("botRoles", bot_roles))

	# Log all errors
	dp.add_error_handler(error)

	# Empieza el bot
	updater.start_polling()

	updater.idle()


if __name__ == '__main__':
	main()






