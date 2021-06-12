from ParseVacancies import parse_vacancies
from LoadDBSkills import load_skill_into_db
from Assessment import make_assessment


if __name__ == '__main__':
    parse_vacancies()
    load_skill_into_db()
    print(make_assessment())




