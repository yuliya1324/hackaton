import sqlite3
import numpy as np
import pandas as pd
import json
import os
from IPython import display


def make_assessment():
    """
        Определяет навыки нужно подтянуть в первую очередь
    """
    print('Выявляем необходимые навыки')
    skills_df = skill_frequency_df()
    most_needed_skills = skills_df['skill_name'].to_list()
    points = self_assessment(most_needed_skills)
    skills_df = calculate_gap(skills_df, points)
    return skills_df


def skill_frequency_df() -> pd.DataFrame:
    """
    Определяет 10 наиболее часто требующихся навыков, частоту их появления и отнормировенную частоту
    """

    # создаём новую таблицу с частотами всех навыков
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    selection_query = """
        SELECT distinct(skill_name), COUNT(*)
        FROM Vacancy_Skill
        GROUP BY skill_name
        ORDER BY COUNT(*) DESC
    """

    skills_df = pd.DataFrame(cur.execute(selection_query), columns=['skill_name', 'count'])
    con.commit()

    # масштабируем частоту появления (приводим к диапозону от 0 до 1)
    skills_df['log_count'] = np.log10(skills_df['count'])
    skills_df['scaled_count'] = (skills_df['log_count'] - min(skills_df['log_count'])) / max(skills_df['log_count'])

    # отбираем из всего множества навыков 10 самых востребованных
    skills_df = skills_df.loc[:10, :]

    return skills_df


def self_assessment(most_needed_skills: list) -> list:
    """
    Функция для получения баллов при самоценке пользователя
    """
    print('Оцените свои навыки по шкале от 1 до 5, где (1-совсем не знаю; '
          '3-хорошо знаю базу, но для остального часто пользуюсь справочной информацией; '
          '5-знаю хорошо и пользуюсь знаниями регулярно).')

    points = [int(input(f'{skill}: ')) for skill in most_needed_skills]
    return points


def calculate_gap(skills_df: pd.DataFrame, points: list) -> pd.DataFrame:
    skills_df.loc[:, 'user_points'] = points

    skills_df['scaled_user_points'] = skills_df['user_points'] / 5

    skills_df['gap'] = skills_df['scaled_user_points'] - skills_df['scaled_count']

    skills_df = skills_df.sort_values(by='gap')
    return skills_df
