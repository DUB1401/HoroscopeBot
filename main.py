from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON, RemoveFolderContent
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
# Создание папок в корневой директории.
MakeRootDirectories(["Attachments", "Data"])

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
	
	# Обработка команды: admin.
	@Bot.message_handler(commands = ["admin"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		Admin = BotProcessor.login(Message.from_user)
		
		# Если пользователь является администратором.
		if Admin == True:
			# Отправка сообщения: меню администратора.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "🔒 Доступ к функциям администрирования: *разрешён*\n\n_Панель администрирования открыта\._",
				parse_mode = "MarkdownV2",
				reply_markup = BuildAdminMenu(BotProcessor)
			)
			
		else:
			# Отправка сообщения: права администратора невалидны.
			Bot.send_message(
				chat_id = Message.chat.id,
				text = "🔒 Доступ к функциям администрирования: *запрещён*",
				parse_mode = "MarkdownV2"
			)
	
	# Обработка команды: start.
	@Bot.message_handler(commands = ["start"])
	def Command(Message: types.Message):
		# Авторизация пользователя.
		BotProcessor.login(Message.from_user)
		# Отправка сообщения: приветствие.
		Bot.send_message(
			Message.chat.id,
			"*Добро пожаловать в «Гороскоп дня»\!*\n\nСамый большой и популярный бот\-астролог в Telegram\.\n\nВыбирай свой знак зодиака и смело смотри прогноз на день\!",
			parse_mode = "MarkdownV2",
			reply_markup = BuildZodiacMenu()
		)
		
	# Обработка команды: unattach.
	@Bot.message_handler(commands=["unattach"])
	def Command(Message: types.Message):
	
		# Если пользователь уже администратор.
		if BotProcessor.login(Message.from_user) == True:
			# Удаление текущих вложений.
			RemoveFolderContent("Attachments")
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
			# Отправка сообщения: приветствие.
			Bot.send_message(
				Message.chat.id,
				"🖼️ *Добавление вложений*\n\nВсе вложения удалены\.",
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True,
				reply_markup = BuildAdminMenu(BotProcessor)
			)
		
	# Обработка текстовых сообщений.
	@Bot.message_handler(content_types = ["text"])
	def TextMessage(Message: types.Message):
		# Авторизация пользователя.
		Admin = BotProcessor.login(Message.from_user)
		# Ожидаемый тип значения.
		ExcpectedValue = BotProcessor.getExpectedType()
		
		# Попытка получения гороскопа.
		Result = BotProcessor.getHoroscope(Message.text)
			
		# Если гороскоп получен.
		if Result != None:
			# Отправка сообщения: гороскоп.
			Bot.send_message(
				Message.chat.id,
				Result,
				parse_mode = "MarkdownV2",
				reply_markup = BuildZodiacMenu()
			)
		
		# Если пользователь является администратором.
		if Admin == True:
		
			# Тип сообщения: текст.
			if ExcpectedValue == ExpectedMessageTypes.Message:
				# Сохранение нового текста.
				Result = BotProcessor.editMessage(Message.html_text)
				# Комментарий.			
				Comment = "Текст сообщения изменён\." if Result == True else EscapeCharacters("Сообщение слишком длинное! Telegram устанавливает следующие лимиты:\n\n4096 символов – обычное сообщение;\n2048 символов – сообщение с вложениями (Premium);\n1024 символа – сообщение с вложениями.")
				# Отправка сообщения: редактирование приветствия завершено.
				Bot.send_message(
					Message.chat.id,
					"✍ *Редактирование сообщения*\n\n" + Comment,
					parse_mode = "MarkdownV2",
					disable_web_page_preview = True,
					reply_markup = BuildAdminMenu(BotProcessor)
				)
				# Установка ожидаемого типа сообщения.
				BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)
				
			# Тип сообщения: команда остановки сбора вложения.
			if ExcpectedValue == ExpectedMessageTypes.Image or ExcpectedValue == ExpectedMessageTypes.Undefined:
				
				# Остановка добавления вложений.
				if Message.text == "🖼️ Медиа (остановить)":
					# Запуск коллекционирования.
					BotProcessor.collect(False)
					# Количество вложений.
					AttachmentsCount = BotProcessor.getAttachmentsCount()
					# Отправка сообщения: добавление вложений.
					Bot.send_message(
						Message.chat.id,
						f"🖼️ *Добавление вложений*\n\nКоличество вложений: {AttachmentsCount}\.",
						parse_mode = "MarkdownV2",
						disable_web_page_preview = True,
						reply_markup = BuildAdminMenu(BotProcessor)
					)
					# Установка ожидаемого типа сообщения.
					BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)

			# Тип сообщения: неопределённый.
			if ExcpectedValue == ExpectedMessageTypes.Undefined:
				
				# Редактирование поста.
				if Message.text == "✍ Редактировать":
					# Отправка сообщения: редактирование приветствия.
					Bot.send_message(
						Message.chat.id,
						"✍ *Редактирование сообщение*\n\nОтправьте мне текст нового сообщения\.",
						parse_mode = "MarkdownV2",
						disable_web_page_preview = True,
						reply_markup = BuildAdminMenu(BotProcessor)
					)
					# Установка ожидаемого типа сообщения.
					BotProcessor.setExpectedType(ExpectedMessageTypes.Message)
				
				# Добавление вложений.
				if Message.text == "🖼️ Медиа":
					# Запуск коллекционирования.
					BotProcessor.collect(True)
					# Отправка сообщения: добавление вложений.
					Bot.send_message(
						Message.chat.id,
						"🖼️ *Добавление вложений*\n\nОтправляйте мне изображения, которые необходимо прикрепить к сообщению, или выполните команду /unattach для удаления всех вложений\.",
						parse_mode = "MarkdownV2",
						reply_markup = BuildAdminMenu(BotProcessor)
					)
					# Установка ожидаемого типа сообщения.
					BotProcessor.setExpectedType(ExpectedMessageTypes.Image)
			
				# Предпросмотр сообщения.
				if Message.text == "🔍 Предпросмотр":
					# Отправка сообщения: предпросмотр сообщения.
					BotProcessor.sendMessage(Message.chat.id)
				
				# Запуск рассылки.
				if Message.text == "📨 Рассылка":
					# Запуск рассылки.
					Result = BotProcessor.mailing()
					# Отправка сообщения: завершение рассылки.
					Bot.send_message(
						Message.chat.id,
						f"📨 *Рассылка завершена*\n\nКоличество отправленных сообщений: {Result}\.",
						parse_mode = "MarkdownV2",
						reply_markup = BuildAdminMenu(BotProcessor)
					)
				
				# Вывод статистики.
				if Message.text == "📊 Статистика":
					# Сбор статистики.
					Result = BotProcessor.getStatistics()
					# Отправка сообщения: статистика.
					Bot.send_message(
						chat_id = Message.chat.id,
						text = Result,
						parse_mode = "MarkdownV2",
						reply_markup = BuildAdminMenu(BotProcessor)
					)
				
				# Выход из панели администрирования.
				if Message.text == "❌ Выход":
					# Отправка сообщения: выход.
					Bot.send_message(
						chat_id = Message.chat.id,
						text = "🔒 Доступ к функциям администрирования: *разрешён*\n\n_Панель администрирования закрыта\._",
						parse_mode = "MarkdownV2",
						reply_markup = BuildZodiacMenu()
					)
					
		# Если введён верный пароль.
		elif Message.text == Settings["password"]: 
			# Выдача прав администратора.
			Admin = BotProcessor.login(Message.from_user, Admin = True)
			# Отправка сообщения: права администратора валидны.
			Bot.send_message(
				Message.chat.id,
				"🔒 Доступ к функциям администрирования: *разрешён*",
				parse_mode = "MarkdownV2"
			)
				
	# Обработка изображений (со сжатием).					
	@Bot.message_handler(content_types=["photo"])
	def MediaAttachments(Message: types.Message):
		# Ожидаемый тип значения.
		ExcpectedValue = BotProcessor.getExpectedType()
		
		# Тип сообщения: вложение.
		if ExcpectedValue == ExpectedMessageTypes.Image:
			# Сохранение изображения.
			DownloadImage(Settings["token"], Bot, Message.photo[-1].file_id)
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined) 

	# Обработка изображений (без сжатия).					
	@Bot.message_handler(content_types=["document"])
	def MediaAttachments(Message: types.Message):
		# Ожидаемый тип значения.
		ExcpectedValue = BotProcessor.getExpectedType()
	
		# Тип сообщения: вложение.
		if ExcpectedValue == ExpectedMessageTypes.Image:
			# Сохранение изображения.
			DownloadImage(Settings["token"], Bot, Message.document.file_id)
			# Установка ожидаемого типа сообщения.
			BotProcessor.setExpectedType(ExpectedMessageTypes.Undefined)				
		
	# Запуск обработки запросов Telegram.
	Bot.infinity_polling(allowed_updates = telebot.util.update_types)
		
