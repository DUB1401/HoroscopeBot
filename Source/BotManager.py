from apscheduler.schedulers.background import BackgroundScheduler
from dublib.Methods import ReadJSON, RemoveHTML, WriteJSON
from Source.Functions import EscapeCharacters
from Source.Horoscope import Horoscope
from telebot import types
from time import sleep

import telebot
import random
import enum
import os

# Типы ожидаемых сообщений.
class ExpectedMessageTypes(enum.Enum):
	
	#---> Статические свойства.
	#==========================================================================================#
	# Неопределённое сообщение.
	Undefined = "undefined"
	# Выборка.
	Sampling = "sampling"
	# Текст сообщения.
	Message = "message"
	# Изображение.
	Image = "image"

# Менеджер данных бота.
class BotManager:
	
	# Сохраняет настройки.
	def __SaveSettings(self):
		# Сохранение настроек.
		WriteJSON("Settings.json", self.__Settings)
		
	# Проверяет, состоит ли пользователь в необходимых чатах.
	def __CheckSubscriptions(self, UserID: str) -> bool:
		# Состояние: состоит ли человек в группе.
		IsSubscripted = False
		# Количество подписок.
		Subscriptions = 0
		
		# Если пользователь определён.
		if UserID in self.__Users["users"].keys():
			
			# Для каждого чата.
			for ChatID in self.__Settings["required-subscriptions"].keys():
				
				try:
					# Получение данных об участнике чата.
					Response = self.__Bot.get_chat_member(ChatID, int(UserID))
					# Если участник, инкремент количества подписок.
					if Response.status in ["admin", "creator", "member"]: Subscriptions += 1
					
				except:
					pass
		
		# Если количество подписок соответствует требуемому.
		if Subscriptions == len(self.__Settings["required-subscriptions"].keys()):
			# Переключение статуса.
			IsSubscripted = True
			# Изменение состояния подписки пользователя.			
			self.__Users["users"][UserID]["subscripted"] = True
			# Сохранение базы данных.
			WriteJSON("Data/Users.json", self.__Users)
		
		return IsSubscripted
	
	# Конструктор.
	def __init__(self, Settings: dict, Bot: telebot.TeleBot):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Планировщик задач.
		self.__Planner = BackgroundScheduler()
		# Текущий тип ожидаемого сообщения.
		self.__ExpectedType = ExpectedMessageTypes.Undefined
		# Словарь гороскопа.
		self.__Horoscope = Horoscope(Settings)
		# Словарь определений пользователь.
		self.__Users = ReadJSON("Data/Users.json")
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Экземпляр бота.
		self.__Bot = Bot
		# Создание задачи по обновлению.
		self.__Planner.add_job(self.__Horoscope.update, "cron", minute = "0", hour = "0")
		# Запуск планировщика.
		self.__Planner.start()
		
	# Переключает сбор изображений.
	def collect(self, Status: bool):
		# Переключение сбора изображений.
		self.__Settings["collect-media"] = Status
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Изменяет текст приветствия.
	def editMessage(self, Text: str) -> bool:
		# Состояние: корректин ли текст.
		IsCorrected = True
		# Максимальная длина сообщения.
		MaxLength = 1024 if self.__Settings["premium"] == False else 2048
		if len(os.listdir("Data")) == 0: MaxLength = 4096 
		
		# Если сообщение слишком длинное.
		if len(RemoveHTML(Text)) >= MaxLength:
			# Отключение бота.
			self.disable()
			# Переключение состояния.
			IsCorrected = False
			
		else:
			# Запись сообщения.
			self.__Settings["message"] = Text
			# Сохранение настроек.
			self.__SaveSettings()
			
		return IsCorrected
	
	# Возвращает количество вложений.
	def getAttachmentsCount(self) -> int:
		# Подсчёт количества файлов.
		Count = len(os.listdir("Attachments"))
		
		return Count
		
	# Возвращает словарь параметров бота.
	def getData(self) -> dict:
		return self.__Settings.copy()
		
	# Возвращает текст гороскопа.
	def getHoroscope(self, UserID: int, Zodiac: str) -> str | None:
		# Разбитие по пробелам.
		Zodiac = Zodiac.split(" ")
		# Получение текста гороскопов.
		Data = self.__Horoscope.getHoroscopes()
		# Текст ответного сообщения.
		Text = None
		
		# Если знак зодиака определён.
		if len(Zodiac) > 1 and Zodiac[1].lower() in list(map(lambda x: x.lower(), list(Data.keys()))):
			
			# Если пользователь состоит во всех обязательных чатах или является администратором.
			if self.__Users["users"][str(UserID)]["subscripted"] == True or self.__Users["users"][str(UserID)]["admin"] == True:
				# Получение знака зодиака.
				Zodiac = Zodiac[1]
				# Текущая дата.
				Date = EscapeCharacters(self.__Horoscope.getDate().split(" ")[0])
				# Формирование заголовка гороскопа.
				Text = f"*Гороскоп на {Date}*\n\n" + Data[Zodiac]["symbol"] + " *" + Zodiac.upper() + "*\n\n"
				# Добавление рубрик гороскопа.
				if Data[Zodiac]["love"] != None: Text += Data[Zodiac]["love"] + "\n\n"
				if Data[Zodiac]["career"] != None: Text += Data[Zodiac]["career"] + "\n\n"
				if Data[Zodiac]["health"] != None: Text += Data[Zodiac]["health"] + "\n\n"
				# Добавление прощания.
				Text += "Удачного вам дня\!"
				
			else:
				# Список кнопок.
				Buttons = types.InlineKeyboardMarkup(row_width = 1)
				
				# Для каждого чата.
				for ChatID in self.__Settings["required-subscriptions"].keys():
					
					try:
						# Кнопка подписки.
						Button = types.InlineKeyboardButton(self.__Settings["required-subscriptions"][ChatID]["title"], url = self.__Settings["required-subscriptions"][ChatID]["link"])
						# Добавление кнопки.
						Buttons.add(Button)
						
					except Exception as ExceptionData:
						# Вывод исключения.
						print(ExceptionData)
					
				# Отправка сообщения: необходима подписка.
				self.__Bot.send_message(
					chat_id = UserID,
					text = self.__Settings["subscription-notification"],
					parse_mode = "HTML",
					reply_markup = Buttons
				)

		return Text

	# Возвращает тип ожидаемого сообщения.
	def getExpectedType(self) -> ExpectedMessageTypes:
		return self.__ExpectedType
	
	# Возвращает статистику.
	def getStatistics(self) -> str:
		# Текст статистики.
		Text = "*📊 Статистика*\n\n"
		# Количество активных пользователей.
		ActiveUsersCount = 0
		# Количество пользователей с подпиской Premium.
		PremiumUsersCount = 0
		
		# Для каждого пользователя.
		for UserID in self.__Users["users"].keys():
			# Если пользователь активен, выполнить инкремент.
			if self.__Users["users"][UserID]["active"] == True: ActiveUsersCount += 1
			# Если пользователь имеет подписку, выполнить инкремент.
			if self.__Users["users"][UserID]["premium"] == True: PremiumUsersCount += 1
			
		# Добавление данных.
		Text += "Активные пользователи: _" + EscapeCharacters(str(ActiveUsersCount)) + "_\n"
		Text += "Имеют Premium: _" + EscapeCharacters(str(PremiumUsersCount) + " (" + str(int(float(PremiumUsersCount / ActiveUsersCount) * 100.0)) + "%)") + "_\n"

		return Text
	
	# Возвращает статус бота.
	def getStatus(self) -> bool:
		return self.__Settings["active"]
	
	# Регистрирует пользователя или обновляет его данные.
	def login(self, User: telebot.types.User, Admin: bool = False) -> bool:
		# Конвертирование ID пользователя.
		UserID = str(User.id) 
		# Буфер данных пользователей.
		Bufer = {
			"first-name": User.first_name,
			"last-name": User.last_name,
			"username": User.username,
			"premium": bool(User.is_premium),
			"subscripted": False,
			"active": True,
			"admin": Admin
		}
		
		# Если пользователь определён.
		if UserID in self.__Users["users"].keys() and Admin == False:
			# Запись статуса администратора, подписки и активности.
			Bufer["admin"] = self.__Users["users"][UserID]["admin"]
			Bufer["subscripted"] = self.__Users["users"][UserID]["subscripted"]
			Bufer["active"] = self.__Users["users"][UserID]["active"]
			
		# Если подписки не выполнены, проверить их статус.
		if Bufer["subscripted"] == False or self.__Settings["always-check-subscriptions"] == True: Bufer["subscripted"] = self.__CheckSubscriptions(UserID)
		# Перезапись данных пользователя.
		self.__Users["users"][UserID] = Bufer	
		# Сохранение базы данных.
		WriteJSON("Data/Users.json", self.__Users)
		
		return Bufer["admin"]
	
	# Запускает рассылку по выборке.
	def mailing(self, Sampling: int) -> int:
		# Количество отправок.
		Mails = 0
		# Выборка пользователей.
		Users = list()
		
		# Если указаны все активные пользователи.
		if Sampling == 0:
			
			# Для каждого пользователя.
			for UserID in self.__Users["users"].keys():
			
				# Если пользователь активен.
				if self.__Users["users"][UserID]["active"] == True: 
					# Записать ID пользователя.
					Users.append(UserID)
					
		# Если выбраны все Premium-пользователи.
		elif Sampling == -1:
			
			# Для каждого пользователя.
			for UserID in self.__Users["users"].keys():
			
				# Если пользователь имеет Premium.
				if self.__Users["users"][UserID]["premium"] == True: 
					# Записать ID пользователя.
					Users.append(UserID)
					
		# Если выбрана случайная часть пользователей.
		elif Sampling > 0:

			# Буфер активных пользователей.
			Bufer = list()
			
			# Для каждого пользователя.
			for UserID in self.__Users["users"].keys():
			
				# Если пользователь активен.
				if self.__Users["users"][UserID]["active"] == True: 
					# Записать ID пользователя.
					Bufer.append(UserID)
			
			# Если запрошена выборка больше, чем определено активных пользователей.
			if Sampling >= len(Bufer):
				# Выбрать всех активных пользователей.
				Users = Bufer
				
			else:
				# Определение случайной выборки.
				Users = random.sample(Bufer, Sampling)

		# Отправить каждому пользователю сообщение.
		for UserID in Users:
			
			# Если пользователь активен.
			if self.__Users["users"][UserID]["active"] == True: 
				# Отправка сообщения.
				self.sendMessage(int(UserID))
				# Инкремент количество отправок.
				Mails += 1
				
			# Выжидание интервала.
			sleep(self.__Settings["delay"])

		return Mails
			
	# Отправляет сообщение.
	def sendMessage(self, ChatID: int):
		# Список файлов.
		Files = os.listdir("Attachments")[:10]
		
		# Если есть вложения.
		if len(Files) > 0:
			# Список медиа вложений.
			Attachments = list()
			
			# Для каждого файла.
			for Index in range(0, len(Files)):
				
				# Дополнить вложения файлом.
				Attachments.append(
					types.InputMediaPhoto(
						open("Attachments/" + Files[Index], "rb"), 
						caption = self.__Settings["message"] if Index == 0 else "",
						parse_mode = "HTML"
					)
				)
				
			try:
				# Отправка медиа группы: приветствие нового подписчика.
				self.__Bot.send_media_group(
					ChatID,
					media = Attachments
				)
				
			except Exception as ExceptionData:
				# Вывод исключения.
				print(ExceptionData)
			
		else:

			# Если сообщение не пустое.
			if len(self.__Settings["message"]) > 0:
				
				try:
					# Отправка сообщения: приветствие нового подписчика.
					self.__Bot.send_message(
						ChatID,
						text = self.__Settings["message"],
						parse_mode = "HTML",
						disable_web_page_preview = True
					)
					
				except Exception as ExceptionData:
					# Вывод исключения.
					print(ExceptionData)

	# Задаёт тип ожидаемого сообщения.
	def setExpectedType(self, Type: ExpectedMessageTypes):
		self.__ExpectedType = Type