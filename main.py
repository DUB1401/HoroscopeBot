from Source.Core.Horoscope import Horoscoper, Zodiacs
from Source.UI import InlineKeyboards, ReplyKeyboards
from Source.Core.Scheduler import Scheduler
from Source.UI.AdminPanel import Panel
from Source.Core.GetText import _

from dublib.TelebotUtils import TeleCache, TeleMaster, UsersManager
from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.Methods.Filesystem import MakeRootDirectories
from dublib.Methods.JSON import ReadJSON
from telebot import types

import telebot
import random
import os

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

CheckPythonMinimalVersion(3, 10)
MakeRootDirectories(["Data/Horoscopes"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК И СОЗДАНИЕ ОБЪЕКТОВ <<<<< #
#==========================================================================================#

Settings = ReadJSON("Settings.json")
if type(Settings["bot_token"]) != str or Settings["bot_token"].strip() == "": raise Exception("Invalid Telegram bot token.")
if type(Settings["bot_name"]) == str: Settings["bot_name"] = Settings["bot_name"].strip("\t \n@")

Bot = telebot.TeleBot(Settings["bot_token"])
MasterBot = TeleMaster(Bot)
Users = UsersManager("Data/Users")
AdminPanel = Panel()

Cacher = TeleCache("TeleCache.json")
Cacher.set_options(Bot, Settings["cache_chat_id"])

Horoscopes = Horoscoper(Cacher)

SchedulerObject = Scheduler(Bot, Users, Horoscopes)
if Settings["update_on_restart"]: SchedulerObject.update_horoscopes()
SchedulerObject.run()

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

AdminPanel.decorators.commands(Bot, Users, Settings["password"])

@Bot.message_handler(commands = ["mailset"])
def Command(Message: types.Message):
	User = Users.auth(Message.from_user)
	Bot.send_message(User.id, _("Желаете включить утреннюю рассылку <b>Гороскопа дня</b>?"), parse_mode = "HTML", reply_markup = InlineKeyboards.notifications())

@Bot.message_handler(commands = ["share"])
def Command(Message: types.Message):
	User = Users.auth(Message.from_user)
	
	QrPath = "Data/Images/qr.jpg"
	BotName = Settings["bot_name"]

	if BotName: BotName = f"@{BotName}\n@{BotName}\n@{BotName}\n\n"
	else: BotName = ""

	Caption = BotName + _("<b>🌟 Гороскоп дня</b>\nНайди свой знак зодиака и узнай, что для тебя на сегодня приготовили звезды!")

	if os.path.exists(QrPath):
		FileID = None

		try: FileID = Cacher[QrPath]
		except KeyError: FileID = Cacher.upload_file(QrPath, types.InputMediaPhoto).id

		Bot.send_photo(User.id, FileID, Caption, parse_mode = "HTML")

	else:
		Bot.send_message(User.id, Caption, parse_mode = "HTML")

@Bot.message_handler(commands = ["start"])
def Command(Message: types.Message):
	User = Users.auth(Message.from_user)
	User.set_property("zodiac", None, force = False)

	Bot.send_message(
		chat_id = Message.chat.id,
		text = _("<b>Добро пожаловать в Гороскоп дня!</b>\n\nСамый большой и популярный бот-астролог в Telegram 💫\n\nВыбирай свой знак зодиака и смело начинай этот день!"),
		parse_mode = "HTML",
		reply_markup = ReplyKeyboards.zodiac_menu()
	)

#==========================================================================================#
# >>>>> ОБРАБОТКА REPLY-КНОПОК <<<<< #
#==========================================================================================#

AdminPanel.decorators.reply_keyboards(Bot, Users)

#==========================================================================================#
# >>>>> ОБРАБОТКА ВВОДА ТЕКСТА <<<<< #
#==========================================================================================#

@Bot.message_handler(content_types = ["text"])
def Text(Message: types.Message):
	User = Users.auth(Message.from_user)
	if AdminPanel.procedures.text(Bot, User, Message): return

	ErrorMessages = [
		_("Пожалуйста, используйте кнопки ниже, для выбора своего знака зодиака"),
		_("Немножко некорректный запрос. Для работы со мной используйте меню внизу)"),
		_("Не могу обработать эту команду. Буду рад, если вы нажмете на свой знак зодиака"),
		_("Очень интересно, но, к сожалению, не знаю, что на это ответить. Попробуйте использовать меню внизу)"),
		_("Это неизвестная для меня команда. Для получения прогноза вам лучше воспользоваться кнопками ниже")
	]

	ErrorMessage = random.choice(ErrorMessages)
	Words = Message.text.split(" ")

	if len(Words) != 2:
		Bot.send_message(User.id, ErrorMessage)
		return

	Zodiac = Words[-1].lower()

	if Zodiac not in [Element.value for Element in Zodiacs]:
		Bot.send_message(User.id, ErrorMessage)
		return
	
	Zodiac = Zodiacs(Zodiac)
	SchedulerObject.send_horoscope(User, Zodiac)

#==========================================================================================#
# >>>>> ОБРАБОТКА INLINE-КНОПОК <<<<< #
#==========================================================================================#

AdminPanel.decorators.inline_keyboards(Bot, Users)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("notifications"))
def InlineButton(Call: types.CallbackQuery):
	User = Users.auth(Call.from_user)
	Command = Call.data.split("_")[-1]

	match Command:

		case "enable":
			Bot.edit_message_text(_("Выберите свой знак зодиака из представленного ниже списка:"), User.id, Call.message.id, reply_markup = InlineKeyboards.zodiac_selector())

		case "disable":
			User.set_property("zodiac", None)
			Bot.edit_message_text(_("Хорошо! Вы в любой момент сможете посмотреть предсказания, нажав на кнопку своего знака зодиака в меню 💫"), User.id, Call.message.id, reply_markup = None)

@Bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("select"))
def InlineButton(Call: types.CallbackQuery):
	User = Users.auth(Call.from_user)
	Value = Call.data.split("_")[-1]
	User.set_property("zodiac", Value)
	Bot.edit_message_text(
		text = _("Спасибо! Теперь вы будете просыпаться вместе со звездами! ✨️"),
		chat_id = User.id,
		message_id = Call.message.id,
		reply_markup = None
	)

#==========================================================================================#
# >>>>> ОБРАБОТКА ФАЙЛОВ <<<<< #
#==========================================================================================#

AdminPanel.decorators.files(Bot, Users)
	
Bot.infinity_polling()