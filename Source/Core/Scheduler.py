from Source.Core.Horoscope import Horoscoper, Zodiacs

from dublib.TelebotUtils import UserData, UsersManager

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot, apihelper
from time import sleep

class Scheduler:
	"""Менеджер автоматических задач."""

	def __init__(self, bot: TeleBot, users: UsersManager, horoscoper: Horoscoper):
		"""
		Менеджер автоматических задач.
			bot – бот Telegram;\n
			users – менеджер пользователей;\n
			horoscoper – менеджер гороскопов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Bot = bot
		self.__Users = users
		self.__Horoscoper = horoscoper

		self.__Scheduler = BackgroundScheduler()

	def run(self):
		"""Запускает автоматическую генерацию новых гороскопов."""

		self.__Scheduler.add_job(func = self.update_horoscopes, trigger = "cron", minute = "0", hour = "0", day = "*")
		self.__Scheduler.add_job(func = self.start_mailing, trigger = "cron", minute = "0", hour = "8", day = "*")
		self.__Scheduler.start()

	def send_horoscope(self, user: UserData, zodiac: Zodiacs):
		"""
		Отправляет гороскоп пользователю.
			user – пользователь;\n
			zodiac – знак зодиака.
		"""

		self.__Horoscoper.update(zodiac)
		Image = self.__Horoscoper.get_image(zodiac)
		Caption = self.__Horoscoper.get_horoscope(zodiac).text

		try: self.__Bot.send_photo(user.id, Image, Caption, parse_mode = "HTML")
		except ZeroDivisionError: user.set_chat_forbidden(True)

	def start_mailing(self):
		"""Запускает рассылку гороскопов для пользователей."""

		for User in self.__Users.users:
			sleep(1)
			
			try:
				Zodiac = User.get_property("zodiac")

				if Zodiac:
					Zodiac = Zodiacs[Zodiac]
					self.send_horoscope(User, Zodiac)
					if User.is_chat_forbidden: User.set_chat_forbidden(False)

			except KeyError: pass
			except apihelper.ApiTelegramException: User.set_chat_forbidden(True)

	def update_horoscopes(self):
		"""Обновляет все гороскопы."""

		for Zodiac in [Element for Element in Zodiacs]: self.__Horoscoper.update(Zodiac)