import sqlite3
import typing

from Assessment import self_assessment
from CheckPythonSkills import check_python_skills
from CoursesLink import offer_courses


def define_skills():
    grade, ocupn = define_goal()
    create_needed_skills_table(grade, ocupn)
    make_assessment()
    give_results()
    offer_courses()
    return None


def get_grades_occupations() -> typing.Tuple[list, list]:
    """
    Из БД находит список профессий и список уровней
    @return: список имеющихся в БД профессий и список уровней
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    occupations = list(cur.execute("SELECT Occupation_Name FROM Occupation"))
    grades = list(cur.execute("SELECT Grade_Name FROM Grade"))

    con.commit()

    return occupations, grades


def define_goal() -> typing.Tuple[int, int]:
    """
    Пользователь выбирает интерисующую профессию и уровень освоения
    @return: ID профессии, ID уровня освоения
    """
    occupations, grades = get_grades_occupations()

    print('Выберите желаемую профессию и введите цифру: ')
    for idx, ocp in enumerate(occupations):
        print(f'{idx + 1} - {ocp[0]}')
    ocupn = int(input('Введите цифру: '))

    print('Выберите желаемый уровень освоения профессии и введите цифру: ')
    for idx, grd in enumerate(grades):
        print(f'{idx + 1} - {grd[0]}')
    grade = int(input('Введите цифру: '))

    print(20 * '-')
    return grade, ocupn


def create_needed_skills_table(grade: int, ocupn: id) -> None:
    """
    Создает таблицу для необходимых навыков.
    @param grade: ID уровня освоения
    @param ocupn: ID профессии
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    needed_skills_table_deletion = """
        DROP TABLE IF EXISTS Needed_Skills
        """

    needed_skills_table_creation = """
        CREATE TABLE IF NOT EXISTS Needed_Skills AS
        SELECT * FROM Occupation_Skills 
        WHERE GradeID = ? AND OccupationID = ?
        LIMIT 5
        """

    cur.execute(needed_skills_table_deletion)
    cur.execute(needed_skills_table_creation, (grade, ocupn))

    con.commit()


def make_assessment() -> None:
    """
        Оценивает пользователя по важным навыкам.
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    needed_skills_names = list(cur.execute("""SELECT Skill_Name FROM Skill 
                                           JOIN Needed_Skills NS on Skill.SkillID = NS.SkillID
                                           ORDER BY ScaledCount DESC"""))

    print('Наиболее востребованными навыками (в порядке убывания важности) '
          'для данной профессии по мнению работодателей являются: ')
    for i, skill_name in enumerate(needed_skills_names):
        print(f'{i + 1}. {skill_name[0]}')
    print(20 * '-')

    cur.execute("ALTER TABLE Needed_Skills ADD UserPoints REAL")
    cur.execute("ALTER TABLE Needed_Skills ADD ScaledUserPoint REAL")
    cur.execute("ALTER TABLE Needed_Skills ADD Gap REAL")

    points = self_assessment(needed_skills_names)

    insert_user_point = """UPDATE Needed_Skills SET UserPoints = ? WHERE Needed_Skills.SkillID = (SELECT SkillID
                            FROM Skill WHERE Skill_Name = ?)"""

    for skill_name in points:
        cur.execute(insert_user_point, (points[skill_name], skill_name[0]))
    con.commit()

    # высчитывем gap между требуемыми навыками и текущими знаниями
    skills_ID = list(cur.execute("SELECT SkillID FROM Needed_Skills"))
    for skill in skills_ID:
        cur.execute("UPDATE Needed_Skills SET ScaledUserPoint = "
                    "(SELECT UserPoints/5 FROM Needed_Skills WHERE SkillID = ?) WHERE SkillID = ?",
                    (skill[0], skill[0]))
        cur.execute("UPDATE Needed_Skills SET Gap = (SELECT ScaledUserPoint-ScaledCount"
                    " FROM Needed_Skills WHERE SkillID = ?) WHERE SkillID = ?", (skill[0], skill[0]))
    con.commit()

    if ('python',) in needed_skills_names:
        check_python_skills()
        print(20 * '-')


def give_results():
    """
    Дает рекомендацию, что нужно изучить в первую очередь.
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    personal_skills_names = list(cur.execute("""SELECT Skill_Name FROM Skill 
                                               JOIN Needed_Skills NS on Skill.SkillID = NS.SkillID
                                               ORDER BY Gap"""))

    print('Учитывая ваши знания, мы рекомедуем в первую очередь развивать следующие навыки:')
    for i, skill_name in enumerate(personal_skills_names):
        print(f'{i + 1}. {skill_name[0]}')
    print(20 * '-')
