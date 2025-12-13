from Source.TeleBotAdminPanel.Modules.Statistics import CellData
from Source.UI import ReplyKeyboards

from dublib.Engine.GetText import _

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils import UserData

	from telebot import TeleBot

#==========================================================================================#
# >>>>> ФУНКЦИЯ ЗАПОЛНЕНИЯ ЯЧЕЙКИ ЗОДИАКА В ВЫГРУЗКЕ <<<<< #
#==========================================================================================#

def get_zodiac(user: "UserData") -> CellData:
	Data = CellData()
	if user.has_property("zodiac") and user.get_property("zodiac"): Data.value = user.get_property("zodiac")
	
	return Data

#==========================================================================================#
# >>>>> CALLBACK-ФУНКЦИЯ ОБРАБОТКИ ЗАКРЫТИЯ ПАНЕЛИ <<<<< #
#==========================================================================================#

def close_callback(user: "UserData", args: tuple):
	Bot: "TeleBot" = args[0]
	Bot.send_message(
		chat_id = user.id,
		text = _("<b>Добро пожаловать в Гороскоп дня!</b>\n\nСамый большой и популярный бот-астролог в Telegram 💫\n\nВыбирай свой знак зодиака и смело начинай этот день!"),
		parse_mode = "HTML",
		reply_markup = ReplyKeyboards.zodiac_menu()
	)