import sqlite3
import json
import os
from IPython import display


def load_skill_into_db() -> None:
    """
        Из сохранённых описаний ваканисий получает необходимые навыки и
        заполняет данные о вакансии и требуемом навыке в базу данных
    """
    data_skills = prepare_skills_data()
    fill_db_skills(data_skills)


def prepare_skills_data() -> list:
    """
        Из сохранённых описаний ваканисий получает необходимые навыки
    """

    # Списки для столбцов таблицы Vacancy_Skill
    data_skills = []

    # общее количество файлов, которые надо обработать
    cnt_docs = len(os.listdir('./vacancies'))

    # Проходимся по всем файлам в папке vacancies
    for fl in os.listdir('./vacancies'):

        # Открываем, читаем и закрываем файл
        f = open(f'./vacancies/{fl}', encoding='utf8')
        json_text = f.read()
        f.close()

        # Текст файла переводим в справочник
        json_obj = json.loads(json_text)

        # Заполняем списки для таблицы
        try:
            for skl in json_obj['key_skills']:
                data_skills.append((json_obj['id'], skl['name']))
        except:
            print(json_obj)

        display.clear_output(wait=True)

    return data_skills


def fill_db_skills(data_skills: list) -> None:
    """
    Заполняет данные о вакансии и требуемом навыке в базу данных
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    vacancy_skill_table_creation = """
    CREATE TABLE IF NOT EXISTS Vacancy_Skill (
        vacancyID INTEGER,
        skill_name TEXT )
    """

    vacancy_skill_table_drop = """
    DELETE FROM Vacancy_Skill
    """

    cur.execute(vacancy_skill_table_creation)
    cur.execute(vacancy_skill_table_drop)

    cur.executemany("INSERT INTO Vacancy_Skill VALUES (?, ?)", data_skills)
    con.commit()
