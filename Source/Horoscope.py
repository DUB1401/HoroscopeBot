from dublib.Methods import ReadJSON, WriteJSON
from freeGPT import Client
from time import sleep

import datetime

from Source.Functions import EscapeCharacters

# Генератор гороскопов.
class Horoscope:
	
	# Возвращает гороскоп.
	def __GetHoroscope(self, Zodiac: str) -> str | None:
		# Вывод в консоль: прогресс.
		print(f"Updating horoscope for zodiac: \"{Zodiac}\"...", end = "")
		# Приведение знака зодиака к нижнему регистру.
		Zodiac = Zodiac.lower()
		# Гороскоп.
		Text = None
		# Составление запроса.
		Request = f"Напиши гороскоп на сегодняшний день для знака зодиака {Zodiac}. Гороскоп должен подходить для публикации и не содержать лишней информации, а также обязательно иметь следующие категории: личная жизнь, карьера, здоровье."
		# Выполнение запроса.
		Response = Client.create_completion(self.__Settings["model"], Request)
		# Интерпретация запроса.
		Text = Response.encode("utf-8").decode("unicode-escape")
		
		# Если произошла ошибка.
		if "Извините" in Text:
			# Вывод в консоль: не удалось.
			print(" Error!")
			
		else:
			# Вывод в консоль: завершение.
			print(" Done.")
		
		return Text
	
	# Конструктор.
	def __init__(self, Settings: dict):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Глобальные настройки.
		self.__Settings = Settings.copy()
	
	# Обновляет гороскопы на сегодняшний день.
	def update(self):
		# Чтение данных гороскопа.
		Data = ReadJSON("Data/Horoscope.json")
		# Запись даты обновления.
		Data["date"] = str(datetime.datetime.now().strftime("%d.%m.%Y"))
		
		# Для каждого знака зодиака.
		for Key in Data["horoscopes"].keys():
			# Получение гороскопа.
			Text = self.__GetHoroscope(Key)
			
			# Для каждого абзаца.
			for Paragraph in Text.split("\n"):
				# Очистка краевых пробельных символов.
				Bufer = EscapeCharacters(Paragraph.strip())
				
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Личная жизнь"):
					# Заполнение поля личной жизни.
					Data["horoscopes"][Key]["love"] = Bufer.replace("Личная жизнь:", "💞 _*Личная жизнь:*_")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Карьера"):
					# Заполнение поля личной жизни.
					Data["horoscopes"][Key]["career"] = Bufer.replace("Карьера:", "💼 _*Карьера:*_")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Здоровье"):
					# Заполнение поля личной жизни.
					Data["horoscopes"][Key]["health"] = Bufer.replace("Здоровье:", "💉 _*Здоровье:*_")

			# Выжидание интервала.
			sleep(self.__Settings["delay"])

		# Запись данных.
		WriteJSON("Data/Horoscope.json", Data)