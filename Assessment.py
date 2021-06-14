import sqlite3
from typing import Union

import numpy as np
import pandas as pd
import translators


def self_assessment(most_needed_skills: list) -> dict:
    """
    Функция для получения баллов при самоценке пользователя
    """
    print('Оцените свои навыки по шкале от 1 до 5, где (1-совсем не знаю; '
          '3-хорошо знаю базу, но для остального часто пользуюсь справочной информацией; '
          '5-знаю хорошо и пользуюсь знаниями регулярно).')

    points = {}
    for skill in most_needed_skills:
        points[skill] = int(input(f'{skill[0]}: '))

    print(20 * '-')
    return points


# def translate_skills(skills_df):
#     eng_skills_names = []
#
#     for skill in skills_df['skill_name'].to_list():
#         output = translators.google(skill, to_language='en', if_use_cn_host=True)
#         eng_skills_names.append(output)
#
#     skills_df.loc[:, 'eng_skill_name'] = eng_skills_names
#     return skills_df