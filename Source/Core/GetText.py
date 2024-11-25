from dublib.Methods.Filesystem import ReadJSON

import gettext

_ = gettext.gettext

try: 
	Settings = ReadJSON("Settings.json")
	_ = gettext.translation("HoroscopeBot", "Locales", languages = [Settings["language"]]).gettext
	
except FileNotFoundError: pass