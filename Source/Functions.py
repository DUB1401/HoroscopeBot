from dublib.Methods import ReadJSON
from telebot import types

# Создаёт разметку меню администратора.
def BuildAdminMenu(Active: bool) -> types.ReplyKeyboardMarkup:
	# Статус бота.
	Status = "🔴 Остановить" if Active == True else "🟢 Возобновить"
	
	# Меню администратора.
	Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
	# Генерация кнопок.
	Exit = types.KeyboardButton("🏃 Выйти")
	Stop = types.KeyboardButton(Status)
	# Добавление кнопок в меню.
	Menu.add(Exit, Stop, row_width = 2)
	
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

# Экранирует символы при использовании MarkdownV2 разметки.
def EscapeCharacters(Post: str) -> str:
	# Список экранируемых символов. _ * [ ] ( ) ~ ` > # + - = | { } . !
	CharactersList = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

	# Экранировать каждый символ из списка.
	for Character in CharactersList:
		Post = Post.replace(Character, "\\" + Character)

	return Post