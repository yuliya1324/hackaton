import sqlite3
import json
import os

from collections import defaultdict, Counter


def prepare_skills_data():
    """
        Из сохранённых описаний ваканисий получает необходимые навыки.
    """

    # Списки для столбцов таблицы Vacancy_Skill
    vacancy_skill = []

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
                vacancy_skill.append((json_obj['id'], str.lower(skl['name'])))
        except:
            print(json_obj)

    # Получаем множество названий всех навыков
    skills = set(obj[1] for obj in vacancy_skill)

    return vacancy_skill, skills


def build_skills_matrix() -> defaultdict:
    """
    Строит и возвращает матрицу смежности навыков.
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    vac_matrix = defaultdict(list)

    vacIDs = list(cur.execute("SELECT DISTINCT(VacancyID) FROM Vacancy_Skill"))
    for vac in vacIDs:
        skills = list(cur.execute("""SELECT Skill_Name FROM Skill
                                     WHERE SkillID IN (SELECT DISTINCT(SkillID)
                                     FROM Vacancy_Skill WHERE VacancyID = ?)""", vac))
        for skill1 in skills:
            for skill2 in skills:
                if skill1[0] != skill2[0]:
                    vac_matrix[skill1[0]].append(skill2[0])
                    vac_matrix[skill2[0]].append(skill1[0].lower())
    con.commit()

    for skill in vac_matrix:
        c = Counter(vac_matrix[skill])
        vac_matrix[skill] = {el: c[el] for el in c if c[el] > 1}

    return vac_matrix
