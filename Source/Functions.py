from dublib.Polyglot import Markdown
from dublib.Methods import ReadJSON
from telebot import types

import requests
import telebot

# Создаёт разметку меню администратора.
def BuildAdminMenu(BotProcessor: any) -> types.ReplyKeyboardMarkup:
	# Статус коллекционирования.
	Collect = "" if BotProcessor.getData()["collect-media"] == False else " (остановить)"
	
	# Меню администратора.
	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	Edit = types.KeyboardButton("✍ Редактировать")
	Add = types.KeyboardButton("🖼️ Медиа" + Collect)
	Preview = types.KeyboardButton("🔍 Предпросмотр")
	Mailing = types.KeyboardButton("📨 Рассылка")
	Statistics = types.KeyboardButton("📊 Статистика")
	Exit = types.KeyboardButton("❌ Выход")
	# Добавление кнопок в меню.
	Menu.add(Edit, Add, Preview, Mailing, Statistics, Exit, row_width = 2)
	
	return Menu

# Создаёт разметку меню рассылки.
def BuildMailingMenu() -> types.ReplyKeyboardMarkup:
	# Меню рассылки.
	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	All = types.KeyboardButton("👤 Все пользователи")
	Premium = types.KeyboardButton("💎 Premium")
	Back = types.KeyboardButton("↩️ Назад")
	# Добавление кнопок в меню.
	Menu.add(All, Premium, Back, row_width = 1)
	
	return Menu

# Создаёт разметку меню выбора знака зодиака.
def BuildZodiacMenu() -> types.ReplyKeyboardMarkup:
	# Чтение гороскопа.
	Data = ReadJSON("Data/Horoscope.json")
	# Меню выбора знака.
	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# Список кнопок строки.
	RowButtons = list()

	# Для каждого знака зодиака.
	for Key in Data["horoscopes"].keys(): 
		# Добавление кнопки.
		RowButtons.append(types.KeyboardButton(Data["horoscopes"][Key]["symbol"] + " " + Key))
		
		# Если в буфере строки 3 кнопки.
		if len(RowButtons) % 3 == 0:
			# Запись строки.
			Menu.row(*RowButtons)
			# Обнуление буфера.
			RowButtons = list()
	
	return Menu

# Загружает изображение.
def DownloadImage(Token: str, Bot: telebot.TeleBot, FileID: int) -> bool:
	# Состояние: успешна ли загрузка.
	IsSuccess = False
	# Получение сведений о файле.
	FileInfo = Bot.get_file(FileID) 
	# Получение имени файла.
	Filename = FileInfo.file_path.split('/')[-1]
	# Список расширений изображений.
	ImagesTypes = ["jpeg", "jpg", "png", "gif"]
	
	# Если вложение имеет расширение изображения.
	if Filename.split('.')[-1] in ImagesTypes:

		# Загрузка файла.
		Response = requests.get("https://api.telegram.org/file/bot" + Token + f"/{FileInfo.file_path}")
	
		# Если запрос успешен.
		if Response.status_code == 200:
		
			# Открытие потока записи.
			with open(f"Attachments/{Filename}", "wb") as FileWriter:
				# Запись файла.
				FileWriter.write(Response.content)
				# Переключение статуса.
				IsSuccess = True		
		
	return IsSuccess

# Экранирует символы при использовании MarkdownV2 разметки.
def EscapeCharacters(Post: str) -> str:
	# Экранирование текста.
	Post = Markdown(Post)
	Post.escape()
	Post = str(Post)
	
	return Post