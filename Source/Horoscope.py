from dublib.Methods import ReadJSON, RemoveRecurringSubstrings, RemoveRegexSubstring, WriteJSON
from Source.Functions import EscapeCharacters
from freeGPT import Client
from time import sleep

import datetime
import random
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
		# Модификаторы настроения.
		Modificators = [
			["(нейтральный)", "(нейтральный)", "(нейтральный)"],
			["(позитивный)", "(позитивный)", "(негативный)"],
			["(нейтральный)", "(нейтральный)", "(негативный)"],
			["(нейтральный)", "(позитивный)", "(негативный)"],
		]
		# Текущий модификатор.
		CurrentModificator = random.choice(Modificators)
		# Перемешивание модификаторов случайным образом.
		random.shuffle(CurrentModificator)
		
		# Составление запроса.
		Request = f"Составь уникальный неповторимый гороскоп на сегодняшний день для знака зодиака {Zodiac}. Гороскоп должен обязательно иметь следующие категории: личная жизнь {CurrentModificator[0]}, карьера {CurrentModificator[1]}, здоровье {CurrentModificator[2]}!"
		
		# Пока не получен удовлетворительный результат.
		while "личная жизнь" not in Text.lower() or "карьера" not in Text.lower() or "здоровье" not in Text.lower():
			# Вывод в консоль: выполнение запроса.
			print(f"Requesting by " + self.__Settings["lib"] + "...")
			
			# Если используется библиотека freeGPT.
			if self.__Settings["lib"] == "freeGPT":
				# Выполнение запроса.
				Response = Client.create_completion("gpt4", Request)
				# Интерпретация запроса.
				Text = Response.encode("utf-8").decode("unicode-escape")
			
			# Если используется библиотека g4f.
			elif self.__Settings["lib"] == "g4f":
				
				try:
					# Выполнение запроса.
					Text = g4f.ChatCompletion.create(model = g4f.models.gpt_4, provider = g4f.Provider.GeekGpt, messages = [{"role": "user", "content": Request}])
					
				except:
					# Выжидание интервала.
					sleep(self.__Settings["delay"])
				
			else:
				# Выброс исключения.
				raise Exception("Unsupported GPT-4 lib: \"" + self.__Settings["lib"] + "\".")
				
		# Вывод в консоль: завершение.
		print("Done.")
		# Удаление модификаторов прогноза.
		Text = RemoveRegexSubstring(Text, ".?\([ПпНн][ое][зг][иа]тивный\):?")
		Text = RemoveRegexSubstring(Text, ".?\([Нн]ейтральный\):?")
		# Очистка маркировки.
		Text = Text.replace("**", "")
		
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
				# Очистка поторяющихся пробелов.
				Bufer = RemoveRecurringSubstrings(Paragraph.strip(), " ")
				# Удаление символов новой строки и экранирование.
				Bufer = EscapeCharacters(Bufer.replace("\n", ""))
				
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Личная жизнь"):
					# Буфер горосокопа.
					Bufer = RemoveRegexSubstring(Bufer, "^[Лл]ичная жизнь").strip(": \n")
					# Если буфер начинается с символа в нижнем регистре, добавить копию идентификатора.
					if Bufer[0].islower() == True: Bufer = "Личная жизнь " + Bufer
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["love"] = "💞 _*Личная жизнь:*_\n" + Bufer
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Карьера"):
					# Буфер горосокопа.
					Bufer = RemoveRegexSubstring(Bufer, "^[Кк]арьера").strip(": \n")
					# Если буфер начинается с символа в нижнем регистре, добавить копию идентификатора.
					if Bufer[0].islower() == True: Bufer = "Карьера " + Bufer
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["career"] = "💼 _*Карьера:*_\n" + Bufer
					
				# Если параграф описывает личную жизнь.
				if Bufer.startswith("Здоровье"):
					# Буфер горосокопа.
					Bufer = RemoveRegexSubstring(Bufer, "^[Зз]доровье").strip(": \n")
					# Если буфер начинается с символа в нижнем регистре, добавить копию идентификатора.
					if Bufer[0].islower() == True: Bufer = "Здоровье " + Bufer
					# Заполнение поля личной жизни.
					self.__Horoscope["horoscopes"][Key]["health"] = "💊 _*Здоровье:*_\n" + Bufer
					
			# Выжидание интервала.
			sleep(self.__Settings["delay"])

		# Сохранение данных.
		WriteJSON("Data/Horoscope.json", self.__Horoscope)