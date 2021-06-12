import sqlite3
import json
import os
from IPython import display

# Создаем списки для столбцов таблицы vacancies
data_vac = []

# Создаем списки для столбцов таблицы skills
data_skills = []

# В выводе будем отображать прогресс
# Для этого узнаем общее количество файлов, которые надо обработать
# Счетчик обработанных файлов установим в ноль
cnt_docs = len(os.listdir('./vacancies'))
i = 0

# Проходимся по всем файлам в папке vacancies
for fl in os.listdir('./vacancies'):

    # Открываем, читаем и закрываем файл
    f = open('./vacancies/{}'.format(fl), encoding='utf8')
    jsonText = f.read()
    f.close()

    # Текст файла переводим в справочник
    jsonObj = json.loads(jsonText)

    # Заполняем списки для таблиц
    try:
        data_vac.append((jsonObj['id'], jsonObj['name'], jsonObj['description']))
        for skl in jsonObj['key_skills']:
            data_skills.append((jsonObj['id'], skl['name']))
    except:
        print(jsonObj)

    # Увеличиваем счетчик обработанных файлов на 1, очищаем вывод ячейки и выводим прогресс
    i += 1
    display.clear_output(wait=True)
    display.display(('Готово {} из {}'.format(i, cnt_docs),))

con = sqlite3.connect('database.db')
cur = con.cursor()

# cur.executemany("INSERT INTO vacancies VALUES (?, ?, ?)", data_vac)
# con.commit()

cur.executemany("INSERT INTO skills VALUES (?, ?)", data_skills)
con.commit()


# Выводим сообщение об окончании программы
display.clear_output(wait=True)
display.display(('Вакансии загружены в БД',))
