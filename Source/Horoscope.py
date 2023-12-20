from dublib.Methods import ReadJSON, RemoveRecurringSubstrings, WriteJSON
from Source.Functions import EscapeCharacters
from freeGPT import Client
from time import sleep

import datetime
import g4f

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
		Request = f"Составь уникальный гороскоп на сегодняшний день для знака зодиака {Zodiac}. Гороскоп должен подходить для публикации и не содержать лишней информации, а также обязательно иметь следующие категории: личная жизнь, карьера, здоровье! Сделай его максимально красивым и неповторимым."
		
		# Пока не получен удовлетворительный результат.
		while "личная жизнь:" not in Text.lower() or "карьера:" not in Text.lower() or "здоровье:" not in Text.lower():
			# Вывод в консоль: выполнение запроса.
			print(f"Requesting by " + self.__Settings["mode"] + "...")
			
			# Если используется библиотека freeGPT.
			if self.__Settings["mode"] == "freeGPT":
				# Выполнение запроса.
				Response = Client.create_completion(self.__Settings["model"], Request)
				# Интерпретация запроса.
				Text = Response.encode("utf-8").decode("unicode-escape")
			
			# Если используется библиотека g4f.
			elif self.__Settings["mode"] == "g4f":
				# Выполнение запроса.
				Text = g4f.ChatCompletion.create(model = g4f.models.gpt_4, messages = [{"role": "user", "content": Request}])
				
			else:
				# Выброс исключения.
				raise Exception("Unsupported GPT-4 lib: \"" + self.__Settings["mode"] + "\".")
				
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
				Bufer = RemoveRecurringSubstrings(Paragraph.strip(), " ")
				# Удаление символов новой строки и экранирование.
				Bufer = EscapeCharacters(Bufer.replace("\n", ""))
				
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Личная жизнь"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["love"] = Bufer.strip().replace("Личная жизнь:", "💞 _*Личная жизнь:*_ ")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Карьера"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["career"] = Bufer.strip().replace("Карьера:", "💼 _*Карьера:*_ ")
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Здоровье"):
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["health"] =  Bufer.strip().replace("Здоровье:", "💉 _*Здоровье:*_ ")
				
			# Выжидание интервала.
			sleep(self.__Settings["delay"])

		# Сохранение данных.
		WriteJSON("Data/Horoscope.json", self.__Horoscope)