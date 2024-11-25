from ..Core.GetText import _

from Source.Core.Horoscope import Zodiacs, ZodiacsSigns

from telebot import types

class InlineKeyboards:
	"""Коллекция генераторов Inline-интерфейса."""

	def __init__(self):
		"""Коллекция генераторов Inline-интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass
	
	def notifications() -> types.InlineKeyboardMarkup:
		"""Строит Inline-интерфейс: подтверждение настройки уведомления."""

		Menu = types.InlineKeyboardMarkup()
		No = types.InlineKeyboardButton(_("Нет"), callback_data = "notifications_disable")
		Yes = types.InlineKeyboardButton(_("Да"), callback_data = "notifications_enable")
		Menu.add(No, Yes, row_width = 2)
		
		return Menu

	def zodiac_selector() -> types.InlineKeyboardMarkup:
		"""Строит Inline-интерфейс: панель выбора знака зодиака."""

		Menu = types.InlineKeyboardMarkup()
		RowButtons = list()

		for Zodiac in ZodiacsSigns: 
			RowButtons.append(types.InlineKeyboardButton(Zodiac.value + " " + Zodiacs[Zodiac.name].value.title(), callback_data = "select_" + Zodiacs[Zodiac.name].name))
			
			if len(RowButtons) % 2 == 0:
				Menu.row(*RowButtons)
				RowButtons = list()
		
		return Menu

class ReplyKeyboards:
	"""Коллекция генераторов Reply-интерфейса."""

	def __init__(self):
		"""Коллекция генераторов Reply-интерфейса."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		pass

	def zodiac_menu() -> types.ReplyKeyboardMarkup:
		"""Строит Reply-интерфейс: панель выбора знака зодиака."""

		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		RowButtons = list()

		for Zodiac in ZodiacsSigns: 
			RowButtons.append(types.KeyboardButton(Zodiac.value + " " + Zodiacs[Zodiac.name].value.title()))
			
			if len(RowButtons) % 3 == 0:
				Menu.row(*RowButtons)
				RowButtons = list()
		
		return Menu