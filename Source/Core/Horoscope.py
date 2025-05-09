from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Methods.Data import RemoveRecurringSubstrings
from dublib.CLI.TextStyler import Styles, TextStyler
from dublib.TelebotUtils.Cache import TeleCache
from dublib.Engine.GetText import _

from datetime import datetime, date
from g4f.client import Client
from telebot import types
from time import sleep

import dateparser
import random
import enum
import os
import re

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Zodiacs(enum.Enum):
	"""Перечисление знаков зодиака."""

	Aries = _("овен")
	Taurus = _("телец")
	Gemini = _("близнецы")
	Cancer = _("рак")
	Leo = _("лев")
	Virgo = _("дева")
	Libra = _("весы")
	Scorpio = _("скорпион")
	Sagittarius = _("стрелец")
	Capricorn = _("козерог")
	Aquarius = _("водолей")
	Pisces = _("рыбы")

class ZodiacsSigns(enum.Enum):
	"""Перечисление символов знаков зодиака."""

	Aries = "♈"
	Taurus = "♉"
	Gemini = "♊"
	Cancer = "♋"
	Leo = "♌"
	Virgo = "♍"
	Libra = "♎"
	Scorpio = "♏"
	Sagittarius = "♐"
	Capricorn = "♑"
	Aquarius = "♒"
	Pisces = "♓"

class Horoscope:
	"""Структура данных гороскопа."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def date(self) -> date:
		"""Дата обновления гороскопа."""

		return self.__Date

	@property
	def text(self) -> str | None:
		"""Текст гороскопа."""

		return self.__Text
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, zodiac: Zodiacs):
		"""
		Структура данных гороскопа.
			zodiac – знак зодиака.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Zodiac = zodiac

		self.__Text = None
		self.__Date = datetime.today().date()
		self.__Path = Path = f"Data/Horoscopes/{zodiac.name}.json"
		
		self.read(exception = False)

	def read(self, exception: bool = True):
		"""
		Считывает данные из JSON.
			exception – указывает, выбрасывать ли исключение.
		"""

		if os.path.exists(self.__Path):
			Data = ReadJSON(self.__Path)
			self.__Date = dateparser.parse(Data["date"]).date()
			self.__Text = Data["text"]

		elif exception: raise FileNotFoundError(self.__Path)

	def save(self):
		"""Сохраняет данные в JSON."""

		Data = {
			"date": str(self.__Date),
			"text": self.__Text
		}
		WriteJSON(self.__Path, Data)

	def set_text(self, text: str):
		"""Задаёт новый текст гороскопа."""

		Goodbye = [
			_("Верь, и все получится!"),
			_("Вы под защитой неба!"),
			_("Знай, что магия звёзд работает!"),
			_("Прекрасного настроения!"),
			_("Звезды следят за вами!"),
			_("Удачного вам дня!"),
			_("Удачного вам сегодня!"),
			_("Да будет так!"),
			_("Плодотворного вам дня!"),
			_("Сделаем этот день вместе!"),
			_("Сияние планет вам в путь!"),
			_("Энергия солнца с вами!"),
			_("Вселенная любит вас!"),
			_("Звезды сегодня на вашей стороне!")
		]

		text = text.replace("*", "")
		text = RemoveRecurringSubstrings(text, "\n")
		text = text.strip()
		Paragraphs = text.split("\n")
		text = ""

		for Paragraph in Paragraphs:
			Words = Paragraph.split(" ")
			Words[0] = "<b>" + Words[0]
			Words[4] = Words[4] + "</b>"
			text += " ".join(Words) + "\n"

		text = text.strip()
		text = text.replace("\n", "\n\n")
		ZodiacSign = ZodiacsSigns[self.__Zodiac.name].value
		ZodiacName = "<b>" + ZodiacSign + " " + self.__Zodiac.value.upper() + "</b>"
		text = "<b>" + _("Гороскоп на") + " " + datetime.today().date().strftime(r"%d.%m.%Y") + f"</b>\n\n{ZodiacName}\n\n{text}"
		text +=  "\n\n<b><i>" + random.choice(Goodbye) + "</i></b>"

		self.__Text = text
		self.__Date = datetime.today().date()
		self.save()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Horoscoper:
	"""Генератор гороскопов."""

	def __IsTextValid(self, text: str) -> bool:
		"""
		Проверяет валидность текста на основе регулярного выражения, исключающего латиницу и иные не кирилические символы.
		  text – проверяемый текст.
		"""

		if self.__Settings["language"] not in ("ru", "rus"): return True

		text = str(text)

		return bool(re.match(r"^[А-Яа-яЁё\s.,:;!?()\-\–«»\"\'\[\]{}]+$", text, re.IGNORECASE))

	def __init__(self, cache: TeleCache, settings: dict):
		"""
		Генератор гороскопов.
			cache – ID чата для отправки кэша;\n
			settings – глобальные настройки.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Cache = cache
		self.__Settings = settings

		self.__Horoscopes: dict[Zodiacs, Horoscope] = dict()
		self.__Client = Client()

		for Zodiac in [Element for Element in Zodiacs]: self.__Horoscopes[Zodiac] = Horoscope(Zodiac)

	def get_horoscope(self, zodiac: Zodiacs) -> Horoscope:
		"""
		Возвращает данные гороскопа.
			zodiac – знак зодиака.
		"""

		return self.__Horoscopes[zodiac]
	
	def get_image(self, zodiac: Zodiacs) -> str:
		"""
		Возвращает ID загруженной в Telegram иллюстрации для знака зодиака.
			zodiac – знак зодиака.
		"""

		ZodiacName = zodiac.name.lower()
		Path = f"Data/Images/{ZodiacName}.jpg"
		CachedFile = self.__Cache.get_real_cached_file(Path, types.InputMediaPhoto)

		return CachedFile.file_id

	def update(self, zodiac: Zodiacs, force: bool = False):
		"""
		Обновляет гороскоп для знака зодиака.
			zodiac – знак зодиака;\n
			force – обновить гороскоп даже при уже сгенерированном для сегодняшнего дня
		"""

		Today = datetime.today().date()
		Horoscope = self.__Horoscopes[zodiac]
		Themes = (
			_("общее течение дня"),
			_("взаимоотношения с людьми"),
			_("личная жизнь"),
			_("карьера"),
			_("финансы"),
			_("фон настроения"),
			_("предостережение"),
			_("совет"),
			_("яркое событие"),
			_("уникальный случай"),
		)
		Modes = (
			_("нейтральный"),
			_("нейтральный"),
			_("нейтральный"),
			_("нейтральный"),
			_("нейтральный"),

			_("позитивный"),
			_("позитивный"),

			_("негативный и позитивный"),
			_("негативный и позитивный"),
			_("негативный и позитивный")
		)

		if not Horoscope.text or Horoscope.date != Today or force:
			Updated = False

			while not Updated:

				try:
					FirstTheme = random.choice(Themes)
					FirstMode = random.choice(Modes)
					SecondTheme = random.choice(Themes)
					SecondMode = random.choice(Modes)
					Request = _("Сгенерируй два абзаца гороскопа на сегодняшний день (не более 450 символов в сумме) для: ") + zodiac.value + ". "
					Request += _("Первый абзац на тему %s имеет %s характер,") % (FirstTheme, FirstMode)
					Request += " "
					Request += _("второй абзац на тему %s имеет %s характер.") % (SecondTheme, SecondMode)
					Request += " "
					Request += _("Не добавляй разметки и ничего лишнего.")
					
					Response = self.__Client.chat.completions.create(model = "gpt-4o", messages = [{"role": "user", "content": Request}])
					Text = Response.choices[0].message.content
					
					if len(Text.split(" ")) > 30 and len(Text) < 500 and self.__IsTextValid(Text) and "\n" in Text:
						self.__Horoscopes[zodiac].set_text(Text)
						print(TextStyler(f"{zodiac.name} horoscope updated.").colorize.green)
						Updated = True

					else:
						print(TextStyler(f"Retrying {zodiac.name} updating...").colorize.yellow)
						sleep(5)

				except Exception as ExceptionData: TextStyler(f"Unable to update {zodiac.name} horoscope! Error: {ExceptionData}", text_color = Styles.Colors.Red).print()