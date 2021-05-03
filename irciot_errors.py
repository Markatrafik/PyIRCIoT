
def irciot_get_common_error_descriptions_(in_human_language):
 if in_human_language == "ru": # Russian Language
  return {
     5: " сек.",
     6: " мин.",
     7: " ч.",
     8: " байт",
     9: ", (попытка: {})",
    10: "Соединение закрыто",
    11: "переподключаемся к ",
    12: "Подключаемся к ",
    13: "Вы используете тестовую часть кода библиотеки" \
      + ", она может быть нестабильной или небезопасной" \
      + ", если Вы не уверены - отключите её",
    15: "Отправка в ",
    16: "Использование: ",
    17: "[<опции>]",
    18: "Проблема при чтении конфигурационного файла",
    19: "Ошибка импорта библиотеки",
    64: "базируется на демонстрационной библиотеке IRC-IoT",
   100: "Неизвестная ошибка",
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
 elif in_human_language == "de": # Deutsch
  return {
     5: " Sek.",
     6: " Min.",
     7: " St.",
     8: " Byte(s)",
     9: ", (Versuch: {})",
    10: "Verbindung geschlossen",
    11: "wiederanschluss an das ",
    12: "Verbindung zum ",
    13: "Sie verwenden den Testteil des Bibliothekscodes" \
      + ", er kann instabil oder unsicher sein" \
      + ", wenn Sie sich nicht sicher sind - deaktivieren Sie ihn",
    15: "Senden an ",
    16: "Verwendung: ",
    17: "[<Optionen>]",
    18: "Problem beim Lesen einer Konfigurationsdatei",
    19: "Fehler beim Importieren",
    64: "basiert auf der IRC-IoT-Demonstrationsbibliothek",
   100: "Unbekannter Fehler",
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

def irciot_get_EL_error_descriptions_(in_human_language):
 if in_human_language == "ru": # Russian Language
  return {
   1000: "Ошибка EL ({}):",
   1001: "Неизвестный язык программирования",
   1002: "Данный язык ещё не поддерживается",
   1003: "Некорректное окружение для языка",
   1004: "Код запрещен общим фильтром",
   1005: "Код запрещен фильтром языка",
   1007: "Некорректный синтаксис для данного языка",
   1008: "Размер кода превысил лимит",
   1009: "Невозможно загрузить требуемые модули",
   1010: "Проблема при исполнении кода",
   1024: "Время выполнения истекло",
   1025: "лексический анализ не пройден",
   1100: "использование типа '{}' не допускается",
   1101: "подстановка команд недопустима",
   1103: "функция '{}' недопустима",
   1121: "оператор 'import' не допускается",
   1122: "конструкция 'import' 'from' недопсутима",
   1131: "имя '{}' зарезерировано",
   1151: "Нераспознаваемый ввод: '{}'"
  }
 elif in_human_language == "de": # Deutsch
  return {
   1000: "EL-Fehler ({}):",
   1001: "Unbekannte Programmiersprache",
   1002: "Diese Sprache wird noch nicht unterstützt",
   1003: "Falsche Umgebung für Programmiersprache",
   1004: "Code durch allgemeinen Filter abgelehnt",
   1005: "Code durch Sprachenfilter abgelehnt",
   1007: "Falsche Syntax für diese Programmiersprache",
   1008: "Die Codegröße hat das Limit überschritten",
   1009: "Problem beim Laden der erforderlichen Module",
   1010: "Es gab ein Problem, als der Code ausgeführt wurde",
   1024: "Zeitüberschreitung bei der Ausführung",
   1025: "lexikalische analyse ausgefallen",
   1100: "Der Typ '{}' ist nicht erlaubt",
   1101: "befehlsersetzung ist nicht erlaubt",
   1103: "Die Funktion '{}' ist nicht erlaubt",
   1121: "Die Answisung 'import' ist nicht erlaubt",
   1122: "Die Anweisung 'import 'from' ist nicht zulässig",
   1131: "Der Name '{}' ist reserviert",
   1151: "Nicht identifizierbare Eingabe: '{}'"
  }
 return {}

def irciot_get_rfc1459_error_descriptions_(in_human_language):
 if in_human_language == "ru": # Russian Language
  return {
   2019: "Предупреждение! Не IRC-IoT сеть: '{}'"
  }
 elif in_human_language == "de": # Deutsch
  return {
   2019: "Warnung! Kein IRC-IoT Netzwerk: '{}'"
  }
 return {}

def irciot_get_rfc2217_error_descriptions_(in_human_language):
 if in_human_language == "ru": # Russian Language
  return {
   3008: "COM порт через сеть"
 }
 elif in_human_language == "de": # Deutsch
  return {
   3008: "COM über Netzwerk"
 }
 return {}

def irciot_get_router_error_descriptions_(in_human_language):
 if in_human_language == "ru": # Russian Language
  return {
   10015: "Маршрутизатор обнаружил дубликат при пересылке сообщения",
   10505: "Отсутствует обязательный параметр для узла в графе маршрутизации",
   10507: "Недопустимое значение обязательного параметра для узла в графе маршрутизации",
   10508: "Неверный параметр направления для узла в графе маршрутизации",
   10601: "Неправильная версия протокола для взаимодействия LMR маршрутизаторов",
   10607: "Невозможно создать LMR, достигнуто максимальное число экземпляров",
   10608: "Неверный идентификатор экземпляра LMR",
   10701: "Неправильная версия протокола для взаимодействия GMR маршрутизаторов",
   10707: "Невозможно создать GMR, достигнуто максимальное число экземпляров",
   10708: "Неверный идентификатор экземпляра GMR"
  }
 elif in_human_language == "de": # Deutsch
  return {
   10015: "Der Router hat beim Weiterleiten der Nachricht ein Duplikat entdeckt",
   10505: "Fehlender erforderlicher Parameter für den Knoten in der Routing-Graph",
   10507: "Unzulässiger Wert eines obligatorischen Parameters für einen Knoten in der Routing-Graph",
   10508: "Flascher Richtungsparameter für einen Knoten in der Routing-Graph",
   10601: "Falsche Protokollversion für die Interkommunikation von LMR-Routern",
   10607: "LMR kann nicht erstellt werden, maximale Anzahl von Instanzen erreicht",
   10608: "Ungültiger LMR-Instanz-Identifikator",
   10701: "Falsche Protokollversion für die Interkommunikation von GMR-Routern",
   10707: "GMR kann nicht erstellt werden, maximale Anzahl von Instanzen erreicht",
   10708: "Ungültiger LMR-Instanz-Identifikator"
  }
 return {}

def irciot_get_all_error_descriptions_(in_human_language):
 if not isinstance(in_human_language, str): return {}
 my_dict = irciot_get_common_error_descriptions_(in_human_language)
 my_dict.update(irciot_get_EL_error_descriptions_(in_human_language))
 my_dict.update(irciot_get_router_error_descriptions_(in_human_language))
 return my_dict

