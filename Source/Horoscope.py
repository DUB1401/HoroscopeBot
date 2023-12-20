from dublib.Methods import ReadJSON, WriteJSON
from freeGPT import Client
from time import sleep

import datetime

from Source.Functions import EscapeCharacters

# Генератор гороскопов.
class Horoscope:
	
	# Возвращает гороскоп.
	def __GetHoroscope(self, Zodiac: str) -> str:
		# Вывод в консоль: прогресс.
		print(f"Updating horoscope for zodiac: \"{Zodiac}\".")
		# Приведение знака зодиака к нижнему регистру.
		Zodiac = Zodiac.lower()
		# Гороскоп.
		Text = ""
		# Составление запроса.
		Request = f"Напиши гороскоп на сегодняшний день для знака зодиака {Zodiac}. Гороскоп должен подходить для публикации и не содержать лишней информации, а также обязательно иметь следующие категории: личная жизнь, карьера, здоровье."
		
		# Пока не получен удовлетворительный результат.
		while "личная жизнь:" not in Text.lower() or "карьера:" not in Text.lower() or "здоровье:" not in Text.lower():
			# Выполнение запроса.
			Response = Client.create_completion(self.__Settings["model"], Request)
			# Интерпретация запроса.
			Text = Response.encode("utf-8").decode("unicode-escape")
			# Вывод в консоль: завершение.
			print("Requesting...")
			
		# Вывод в консоль: завершение.
		print("Done.")
		
		return Text
	
	# Конструктор.
	def __init__(self, Settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = Settings.copy()
		# Чтение файла гороскопа.
		self.__Horoscope = ReadJSON("Data/Horoscope.json")
		
	# Возвращает строковую дату.
	def getDate(self) -> str:
		return self.__Horoscope["date"]

	# Возвращает тексты гороскопов.
	def getHoroscopes(self) -> dict:
		return self.__Horoscope["horoscopes"]
	
	# Обновляет гороскопы на сегодняшний день.
	def update(self):
		# Запись даты обновления.
		self.__Horoscope["date"] = str(datetime.datetime.now().strftime("%d.%m.%Y"))
		
		# Для каждого знака зодиака.
		for Key in self.__Horoscope["horoscopes"].keys():
			# Получение гороскопа.
			Text = self.__GetHoroscope(Key)
			
			# Для каждого абзаца.
			for Paragraph in Text.split("\n\n"):
				# Очистка краевых пробельных символов.
				Bufer = EscapeCharacters(Paragraph.strip())
				
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Личная жизнь"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["love"] = Bufer.replace("Личная жизнь:", "💞 _*Личная жизнь:*_")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Карьера"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["career"] = Bufer.replace("Карьера:", "💼 _*Карьера:*_")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Здоровье"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["health"] = Bufer.replace("Здоровье:", "💉 _*Здоровье:*_")

			# Выжидание интервала.
			sleep(self.__Settings["delay"])

		# Сохранение данных.
		WriteJSON("Data/Horoscope.json", self.__Horoscope)