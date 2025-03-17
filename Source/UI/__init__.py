from Source.Core.Horoscope import Zodiacs, ZodiacsSigns

from dublib.Engine.GetText import _
from dublib.Polyglot import HTML

from telebot import types

class InlineKeyboards:
	"""Коллекция генераторов Inline-интерфейса."""
	
	def delete(label: str) -> types.InlineKeyboardMarkup:
		"""Строит Inline-интерфейс: панель выбора знака зодиака."""

		Menu = types.InlineKeyboardMarkup()
		Menu.add(types.InlineKeyboardButton(label, callback_data = "delete"))

		return Menu

	def notifications() -> types.InlineKeyboardMarkup:
		"""Строит Inline-интерфейс: подтверждение настройки уведомления."""

		Menu = types.InlineKeyboardMarkup()
		No = types.InlineKeyboardButton(_("Отключить") + " ❌️", callback_data = "notifications_disable")
		Yes = types.InlineKeyboardButton(_("Настроить") + " ✅", callback_data = "notifications_enable")
		Menu.add(No, Yes, row_width = 2)
		
		return Menu

	def share(self, bot_name: str) -> types.InlineKeyboardMarkup:
		"""
		Строит Inline-интерфейс: кнопка поделиться.
			bot_name – название бота.
		"""

		Menu = types.InlineKeyboardMarkup()
		BotNames = f"\n@{bot_name}\n@{bot_name}\n\n"
		Text = BotNames + HTML(_("<b>🌟 Гороскоп дня</b>\nНайди свой знак зодиака и узнай, что для тебя на сегодня приготовили звезды!\n\n<b><i>Пользуйся и делись с друзьями!</i></b>")).plain_text
		Share = types.InlineKeyboardButton(_("Поделиться"), switch_inline_query = Text)
		Menu.add(Share)

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