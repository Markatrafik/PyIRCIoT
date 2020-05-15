
def irciot_get_common_error_descriptions_(in_human_language):
 if in_human_language == "RU": # Russian Language
  return {
   101: "Несоответствие версии протокола",
   102: "Несоответствие версии библиотеки",
   103: "Недопустимый поля 'dp' при дефрагментации",
   104: "Несоответствие содержания",
   111: "Нет тега 'op' при дефрагментации",
   112: "Нет тега 'dp' при дефрагментации",
   113: "Нет тега 'bp' при дефрагментации",
   121: "Превышено значение поля 'oc'",
   122: "Превышено значение поля 'dc'",
   123: "Превышено значение поля 'bc'",
   131: "Несовпадение пересекающихся фрагментов",
   133: "Несоответствие содержания дефрагментации",
   251: "Проблема декодирования BASE64",
   252: "Проблема декодирования BASE32",
   253: "Проблема декодирования BASE85",
   254: "Проблема декодирования BASE122",
   300: "Метод шифрования ещё не реализован",
   301: "Неверный заголовок Zlib",
   303: "Неполный блок Zlib",
   351: "Неверный формат ключа RSA",
   501: "Неверный формат сообщения IRC-IoT",
   503: "Неверный формат адреса IRC-IoT",
   701: "Проблема при загрузке модуля Zlib",
   702: "Проблема при загрузке модуля BZIP2",
   731: "Проблема при загрузке модуля RSA",
   732: "Проблема при загрузке модуля AES",
   733: "Проблема при загрузке модуля Twofish",
   735: "Проблема при загрузке модуля ГОСТ 3410",
   737: "Проблема при загрузке модуля ГОСТ 3411",
   755: "Проблема при загрузке модуля UserSign",
   777: "Проблема при загрузке модуля UserCrypt",
   811: "Подтверждено по Локальному Словарю",
   812: "Ошибка проверки по Локальному Словарю"
  }
 elif in_human_language == "DE": # Deutsch
  return {
   101: "Nicht übereinstimmende protokollversion",
   102: "Nicht übereinstimmende bibliotheksversion",
   251: "Problem beim dekodieren von BASE64",
   252: "Problem beim dekodieren von BASE32",
   253: "Problem beim dekodieren von BASE85",
   254: "Problem beim dekodieren von BASE122",
   300: "Verschlüsselungsmethode nicht implementiert",
   303: "Unvollständiger Zlib block",
   351: "Falsches RSA schlüsselformat",
   501: "Falsches IRC-IoT nachrichtenformat",
   503: "Falsches IRC-IoT adressformat",
   701: "Problem beim Laden des Moduls Zlib",
   702: "Problem beim Laden des Moduls BZIP2",
   731: "Problem beim Laden des Moduls RSA",
   732: "Problem beim Laden des Moduls AES",
   733: "Problem beim Laden des Moduls Twofish",
   735: "Problem beim Laden des Moduls GOST3410",
   737: "Problem beim Laden des Moduls GOST3411",
   755: "Problem beim Laden des Moduls UserSign",
   777: "Problem beim Laden des Moduls UserCrypt"
  }
 return {}

def irciot_get_router_error_descriptions_(in_human_language):
 if in_human_language == "RU": # Russian Language
  return {
   10015: "Маршрутизатор обнаружил дубликат при пересылке сообщения",
   10505: "Отсутствует обязательный параметр для узла в графе маршрутизации",
   10507: "Недопустимое значение обязательного параметра для узла в графе маршрутизации",
   10508: "Неверный параметр направления для узла в графе маршрутизации",
  }
 if in_human_language == "DE": # Deutsch
  return {
 }
 return {}

