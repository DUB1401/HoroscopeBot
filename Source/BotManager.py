from dublib.Methods import ReadJSON, WriteJSON
from Source.Functions import EscapeCharacters

import telebot
import enum

# Типы ожидаемых сообщений.
class ExpectedMessageTypes(enum.Enum):
	
	#---> Статические свойства.
	#==========================================================================================#
	# Неопределённое сообщение.
	Undefined = "undefined"
	# Текст сообщения.
	Message = "message"
	# Название кнопки.
	Button = "button"
	# Изображение.
	Image = "image"
	# Ссылка кнопки.
	Link = "link"

# Менеджер данных бота.
class BotManager:
	
	# Сохраняет настройки.
	def __SaveSettings(self):
		# Сохранение настроек.
		WriteJSON("Settings.json", self.__Settings)
	
	# Конструктор.
	def __init__(self, Settings: dict, Bot: telebot.TeleBot):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Текущий тип ожидаемого сообщения.
		self.__ExpectedType = ExpectedMessageTypes.Undefined
		# Словарь гороскопа.
		self.__Horoscope = ReadJSON("Data/Horoscope.json")
		# Словарь определений пользователь.
		self.__Users = ReadJSON("Data/Users.json")
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Экземпляр бота.
		self.__Bot = Bot
		
	# Отключает бота.
	def disable(self):
		# Переключение активности.
		self.__Settings["active"] = False
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Включает бота.
	def enable(self):
		# Переключение активности.
		self.__Settings["active"] = True
		# Сохранение настроек.
		self.__SaveSettings()
		
	# Возвращает текст гороскопа.
	def getHoroscope(self, Zodiac: str) -> str:
		# Текущая дата.
		Date = EscapeCharacters(self.__Horoscope["date"].split(" ")[0])
		# Формирование заголовка гороскопа.
		Text = f"*Гороскоп на {Date}*\n\n🔮 *" + Zodiac.upper() + "*\n\n"
		# Добавление рубрик гороскопа.
		if self.__Horoscope["horoscopes"][Zodiac]["love"] != None: Text += self.__Horoscope["horoscopes"][Zodiac]["love"] + "\n\n"
		if self.__Horoscope["horoscopes"][Zodiac]["career"] != None: Text += self.__Horoscope["horoscopes"][Zodiac]["career"] + "\n\n"
		if self.__Horoscope["horoscopes"][Zodiac]["health"] != None: Text += self.__Horoscope["horoscopes"][Zodiac]["health"] + "\n\n"

		return Text

	# Возвращает тип ожидаемого сообщения.
	def getExpectedType(self) -> ExpectedMessageTypes:
		return self.__ExpectedType
	
	# Возвращает статус бота.
	def getStatus(self) -> bool:
		return self.__Settings["active"]
	
	# Выполняет авторизацию администратора.
	def login(self, UserID: int, Password: str | None = None) -> bool:
		# Состояние: является ли пользователь администратором.
		IsAdmin = False

		# Если пользователь уже администратор.
		if Password == None and UserID in self.__Settings["admins"]:
			# Разрешить доступ к функциям.
			IsAdmin = True
			
		return IsAdmin
	
	# Регистрирует пользователя в качестве администратора.
	def register(self, UserID: int):
		# Добавление ID пользователя в список администраторов.
		self.__Settings["admins"].append(UserID)
		# Сохранение настроек.
		self.__SaveSettings()
	
	# Задаёт тип ожидаемого сообщения.
	def setExpectedType(self, Type: ExpectedMessageTypes):
		self.__ExpectedType = Type