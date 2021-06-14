import sqlite3
import numpy as np
from typing import Tuple

from ExtractSkills import prepare_skills_data
from ParseVacancies import parse_vacancies
from DefineSkills import get_grades_occupations


def create_structure() -> None:
    """
    Cоздаёт структуру базы данных.
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    grade_table_creation = """
        CREATE TABLE IF NOT EXISTS Grade (
            GradeID INTEGER PRIMARY KEY,
            Grade_Name TEXT);
            """

    grade_table_deletion = f"""
    DROP TABLE IF EXISTS Grade;
    """
    cur.execute(grade_table_deletion)

    grade_table_filling = """
        INSERT INTO Grade (Grade_Name)
        VALUES('Junior'),
        ('Middle'),
        ('Senior');
        """

    cur.execute(grade_table_creation)
    cur.execute(grade_table_filling)

    occupation_table_deletion = f"""
        DROP TABLE IF EXISTS Occupation;
        """
    cur.execute(occupation_table_deletion)

    occupation_table_creation = """
        CREATE TABLE IF NOT EXISTS Occupation (
            OccupationID INTEGER PRIMARY KEY,
            Occupation_Name TEXT);
            """

    occupation_table_filling = """
        INSERT INTO Occupation (Occupation_Name)
        VALUES('Data Scientist'),
        ('Бизнес-аналитик'),
        ('Backend разработчик');
        """

    cur.execute(occupation_table_creation)
    cur.execute(occupation_table_filling)

    skill_table_creation = """
        CREATE TABLE IF NOT EXISTS Skill (
            SkillID INTEGER PRIMARY KEY,
            Skill_Name TEXT UNIQUE);
            """
    cur.execute(skill_table_creation)

    vacancy_skill_table_creation = """
     CREATE TABLE IF NOT EXISTS Vacancy_Skill (
         GradeID INTEGER,
         OccupationID INTEGER,
         VacancyID INTEGER,
         SkillID INTEGER,
         FOREIGN KEY (GradeID) REFERENCES Grade(GradeID),
         FOREIGN KEY (OccupationID) REFERENCES Occupation(OccupationID),
         FOREIGN KEY (SkillID) REFERENCES Skill(SkillID)
          )
     """
    cur.execute(vacancy_skill_table_creation)

    con.commit()
    print('Стркутура создана...')


def fill_skill_table(skills: list) -> None:
    """
    Заполняет таблицу Skills тегами(навыками), собранными из вакансий
    @param skills: навыки
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    insert_new_skill = """INSERT OR IGNORE INTO Skill(Skill_Name) 
                VALUES(?)"""

    for skill in skills:
        cur.execute(insert_new_skill, (skill,))

    con.commit()


def fill_vacancy_skill_table(occupation: str, grade: str, vacancy_skill: list) -> None:
    """
    Заполняет данные о вакансии и требуемом навыке в базу данных
    @param occupation: ID профессии
    @param grade: ID уровня
    @param vacancy_skill: данные ID вакансии - название навыка
     """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    grade_ID = cur.execute("SELECT GradeID FROM Grade WHERE Grade_Name = ?", grade).fetchone()[0]
    occupation_ID = cur.execute("SELECT OccupationID FROM Occupation"
                                " WHERE Occupation_Name = ?", occupation).fetchone()[0]

    for elem in vacancy_skill:
        skill_name = tuple([elem[1]])
        skill_ID = cur.execute("SELECT SkillID FROM Skill WHERE Skill_Name = ?", skill_name)
        skill_ID = skill_ID.fetchone()[0]

        vac_ID = int(elem[0])
        cur.execute("INSERT INTO Vacancy_Skill VALUES (?,?,?,?)", (grade_ID, occupation_ID, vac_ID, skill_ID))

    con.commit()


def occupation_skills_table() -> None:
    """
    Cоздаёт таблицу Occupation_Skills и заполняет её отнормированными частотами по каждой профессии
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    con.create_function('log2', 1, np.log2)

    occupation_skills_table_deletion = f"""
            DROP TABLE IF EXISTS Occupation_Skills;
            """
    cur.execute(occupation_skills_table_deletion)

    occupation_skills_table_creation = """
        CREATE TABLE IF NOT EXISTS Occupation_Skills AS
        SELECT
            GradeID,
            OccupationID,
            SkillID,
            Count,
            (LogCount- MinLogCount)/ MaxLogCount AS ScaledCount
            FROM (
                SELECT
                GradeID,
                OccupationID,
                SkillID,
                Count,
                log2(Count) AS LogCount,
                MIN(log2(Count)) OVER (PARTITION BY GradeID,OccupationID) AS MinLogCount,
                MAX(log2(Count)) OVER (PARTITION BY GradeID,OccupationID) AS MaxLogCount
                FROM (
                    SELECT
                    GradeID,
                    OccupationID,
                    SkillID,
                    COUNT(SkillID) as Count
                    FROM Vacancy_Skill
                    GROUP BY GradeID,OccupationID,SkillID
                    ORDER BY OccupationID,GradeID, COUNT(SkillID) DESC) AS temp_ocup_skill) AS temp_calc
    """

    cur.execute(occupation_skills_table_creation)

    con.commit()


def load_db() -> None:
    """
    Создает стркутуру базы данных и заполняет таблицы информацией о навыках и ваканисях
    """
    con = sqlite3.connect('database.db')

    create_structure()

    occupations, grades = get_grades_occupations()

    for o in occupations:
        for g in grades:
            grade_occupation = g + o
            print(f'Собираем данные для {grade_occupation}')
            parse_vacancies(grade_occupation)
            vacancy_skill, skills = prepare_skills_data()
            fill_skill_table(skills)
            fill_vacancy_skill_table(o, g, vacancy_skill)

    occupation_skills_table()


load_db()
