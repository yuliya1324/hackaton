import sqlite3
import pandas as pd
from sklearn.linear_model import LogisticRegression
import inquirer

con = sqlite3.connect('database.db')
cur = con.cursor()


def get_occup():
    query = """
    SELECT *
    FROM Occupation 
    """
    return pd.read_sql_query(query, con=con)


def get_skills():
    skills_query = """
    SELECT S.SkillID, Skill_Name
    FROM Needed_Skills JOIN Skill S on Needed_Skills.SkillID = S.SkillID
    """
    skills = pd.read_sql_query(skills_query, con=con)
    cols = list(skills['SkillID'])
    cols.append('prof')
    X = pd.DataFrame(columns=cols)
    return skills, cols, X


def get_vac_skills(skills_freq):
    vacancy_skills_query = """
    SELECT OccupationID, VacancyID, SkillID
    FROM Vacancy_Skill
    """
    vacancy_skills = pd.read_sql_query(vacancy_skills_query, con=con)
    vacancy_skills = vacancy_skills.drop(i[0] for i in vacancy_skills.iterrows() if i[1]['SkillID'] not in skills_freq)
    return pd.concat([vacancy_skills.groupby(['VacancyID']).agg({"SkillID": list}),
                      vacancy_skills[['VacancyID', 'OccupationID']].drop_duplicates().set_index('VacancyID')], axis=1)


def fill_data(X, vacancy_skills):
    for row in vacancy_skills.iterrows():
        prof_name = int(row[1]['OccupationID'])
        skills_list = row[1]['SkillID']
        r = {x: 0 for x in X.columns}
        r['prof'] = prof_name
        for c in skills_list:
            r[c] = 1
        X = X.append(r, ignore_index=True)
    return X


def teach_model(X):
    y = X['prof']
    X = X.drop(columns=['prof'])
    y = y.astype('int')
    clf = LogisticRegression(solver='sag', max_iter=100, random_state=42, multi_class='multinomial').fit(X, y)
    return clf


def predict(mod, features, occupations):
    prof = mod.predict(features)
    return occupations[occupations['OccupationID'] == prof[0]]['Occupation_Name'].values[0]


def get_skills_student(skills, skills_nums):
    questions = [
        inquirer.Checkbox('skills',
                          message='Какими навыками вы обладаете? (Стрелки "вверх" и "вниз" - перемещение по навыкам, '
                                  'стрека "вправо" - выбрать навык, стрека "влево" - отменить выбор навык, '
                                  '"Enter" - закончить выбор)',
                          choices=list(skills['Skill_Name']),
                          ),
    ]
    answers = inquirer.prompt(questions)
    student = answers['skills']
    features = []
    for s in student:
        features.append(skills[skills['Skill_Name'] == s]['SkillID'].values[0])
    vector = pd.DataFrame(columns=skills_nums)
    r = {x: 0 for x in vector.columns}
    for c in features:
        r[c] = 1
    vector = vector.append(r, ignore_index=True)
    return vector.drop(['prof'], axis=1)


def predict_occupation():
    occupations = get_occup()
    skills, skills_nums, data = get_skills()
    vacancy_skills = get_vac_skills(skills_nums)
    data = fill_data(data, vacancy_skills)
    model = teach_model(data)
    student_skills = get_skills_student(skills, skills_nums)
    recommendation = predict(model, student_skills, occupations)
    return recommendation

