
def irciot_get_common_error_descriptions_(in_human_language):
 if in_human_language == "RU": # Russian Language
  return {
   101: "Несоответствие версии протокола",
   102: "Несоответствие версии библиотеки",
   103: "Недопустимое значение поля 'dp' при дефрагментации",
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
   101: "Nicht übereinstimmende Protokollversion",
   102: "Nicht übereinstimmende Bibliotheksversion",
   103: "Falscher 'dp'-Feldwert während der Defragmentierung",
   104: "Inhaltliche Inkonsistenz",
   111: "Es gibt keinen 'op'-Tag für die Defragmentierung",
   112: "Es gibt keinen 'dp'-Tag für die Defragmentierung",
   113: "Es gibt keinen 'bp'-Tag für die Defragmentierung",
   121: "Feldwert 'oc' überschritten",
   122: "Feldwert 'dc' überschritten",
   123: "Feldwert 'bc' überschritten",
   251: "Problem beim dekodieren von BASE64",
   252: "Problem beim dekodieren von BASE32",
   253: "Problem beim dekodieren von BASE85",
   254: "Problem beim dekodieren von BASE122",
   300: "Verschlüsselungsmethode nicht implementiert",
   303: "Unvollständiger Zlib Block",
   351: "Falsches RSA Schlüsselformat",
   501: "Falsches IRC-IoT Nachrichtenformat",
   503: "Falsches IRC-IoT Adressformat",
   701: "Problem beim Laden des Moduls Zlib",
   702: "Problem beim Laden des Moduls BZIP2",
   731: "Problem beim Laden des Moduls RSA",
   732: "Problem beim Laden des Moduls AES",
   733: "Problem beim Laden des Moduls Twofish",
   735: "Problem beim Laden des Moduls GOST3410",
   737: "Problem beim Laden des Moduls GOST3411",
   755: "Problem beim Laden des Moduls UserSign",
   777: "Problem beim Laden des Moduls UserCrypt",
   811: "Bestätigt mit dem Lokalen Wörterbuch",
   812: "Validierungsfehler mit dem Lokalen Wörterbuch"
  }
 return {}

def irciot_get_EL_error_descriptions_(in_humnan_language):
 if in_human_language == "RU": # Russian Language
  return {
   1001: "Неизвестный язык программирования";
   1002: "Данный язык ещё не поддерживается",
   1003: "Некорректное окружение для языка",
   1004: "Код запрещен общим фильтром",
   1005: "Код запрещен фильтром языка",
   1007: "Некорректный синтаксис для данного языка",
   1008: "Размер кода превысил лимит",
   1009: "Невозможно загрузить требуемые модули",
   1010: "Проблема при исполнении кода"
  }
 return {}

def irciot_get_router_error_descriptions_(in_human_language):
 if in_human_language == "RU": # Russian Language
  return {
   10015: "Маршрутизатор обнаружил дубликат при пересылке сообщения",
   10505: "Отсутствует обязательный параметр для узла в графе маршрутизации",
   10507: "Недопустимое значение обязательного параметра для узла в графе маршрутизации",
   10508: "Неверный параметр направления для узла в графе маршрутизации"
  }
 if in_human_language == "DE": # Deutsch
  return {
   10015: "Der Router hat beim Weiterleiten der Nachricht ein Duplikat entdeckt",
   10505: "Fehlender erforderlicher Parameter für den Knoten in der Routing-Graph",
   10507: "Unzulässiger Wert eines obligatorischen Parameters für einen Knoten in der Routing-Graph"
   10508: "Flascher Richtungsparameter für einen Knoten in der Routing-Graph"
  }
 return {}

def irciot_get_all_error_descriptions_(in_human_langauge):
 my_dict = irciot_get_common_error_descriptions_(in_human_language)
 my_dict.update(irciot_get_EL_error_descriptions_(in_human_language)
 my_dict.update(irciot_get_router_error_descriptions_(in_human_lagugage)
 return my_dict

