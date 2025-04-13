
from Source.UI.TeleBotAdminPanel.Extractor import Extractor, CellData

from dublib.TelebotUtils import UserData

#==========================================================================================#
# >>>>> ДОБАВЛЕНИЕ В ВЫПИСКУ ДОПОЛНИТЕЛЬНЫХ КОЛОНОК <<<<< #
#==========================================================================================#

def get_zodiac(user: UserData) -> CellData:

	Data = CellData()
	if user.has_property("zodiac") and user.get_property("zodiac"): Data.value = user.get_property("zodiac")
	
	return Data

Extractor.Columns["Zodiac"] = get_zodiac