#!/usr/bin/python

from dublib.Methods import CheckPythonMinimalVersion, ReadJSON
from Source.Horoscope import Horoscope
from dublib.Terminalyzer import *
from Source.BotManager import *
from Source.Functions import *
from telebot import types

import telebot

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")
# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "": raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: update.
COM_update = Command("update")
CommandsList.append(COM_update)

# Создание команды: start.
COM_start = Command("start")
CommandsList.append(COM_start)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд. 
CommandDataStruct = CAC.checkCommands(CommandsList)

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: update.
if CommandDataStruct != None and "update" == CommandDataStruct.Name:
	# Инициализация сборщика.
	Updater = Horoscope(Settings)
	# Сбор списка алиасов тайтлов, подходящих под фильтр.
	Updater.update()
	
# Запуск Telegram бота.
else:
	# Токен для работы определенного бота телегамм.
	Bot = telebot.TeleBot(Settings["token"])
	# Менеджер данных бота.
	BotProcessor = BotManager(Settings, Bot)
	
	# Обработка команды: start.
	@Bot.message_handler(commands = ["start"])
	def Command(Message: types.Message):
		# Регистрация пользователя.
		BotProcessor.register(Message.from_user)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			"*Добро пожаловать в «Гороскоп дня»\!*\n\nСамый большой и популярный бот\-астролог в Telegram\.\n\nВыбирай свой знак зодиака и смело смотри прогноз на день\!",
			parse_mode = "MarkdownV2",
			reply_markup = BuildZodiacMenu()
		)
		
	# Обработка текстовых сообщений.
	@Bot.message_handler(content_types = ["text"])
	def TextMessage(Message: types.Message):
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			BotProcessor.getHoroscope(Message.text.split(" ")[1]),
			parse_mode = "MarkdownV2",
			reply_markup = BuildZodiacMenu()
		)
		
	# Запуск обработки запросов Telegram.
	Bot.infinity_polling(allowed_updates = telebot.util.update_types)
		
