import sqlite3

from selenium import webdriver
import re
from collections import defaultdict

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ExtractSkills import build_skills_matrix

driver = webdriver.Chrome()


def map_user_level(level: int, sourse: str):
    sourse_level_mapping = {'coursera': ['Начальный', 'Средний', 'Продвинутый'],
                            'harvard': ['Introductory', 'Intermediate', 'Advanced']}

    if level == 1:
        level = sourse_level_mapping[sourse][1]
    elif level in [2, 3]:
        level = sourse_level_mapping[sourse][1]
    else:
        level = sourse_level_mapping[sourse][1]
    return level


def get_courses_harvard(skill, level, matrix):
    skill = skill.lower()
    result = defaultdict(dict)

    level = map_user_level(level, sourse='harvard')

    driver.get(f'https://online-learning.harvard.edu/catalog?keywords={skill}&op=Search')
    h_page = driver.page_source
    for src in ['https://online-learning.harvard.edu'+x for x in re.findall('<h3><a href="(.+?)">', h_page)]:
        driver.get(src)
        src_page = driver.page_source
        level_src = re.findall('Difficulty</div><div class="field">(.+?)</div>', src_page)[0]
        if level_src == level:
            tags = [re.findall('>(.+?)</a>', x)[0].lower() for x in re.findall('<li class="topic-tag">(.+?)</li>', src_page)]
            relevant = 0
            if skill in matrix:
                for tag in tags:
                    if tag in matrix[skill]:
                        relevant += 1
                        break
            if relevant/len(tags) > 0.1:
                name = re.findall('<h1>(.+?)</h1>', src_page)[0]
                result[name]['link'] = src
                result[name]['tags'] = tags
    return result


def get_coursera_courses(skill, level):
    skill = skill.lower()
    result = defaultdict(dict)

    level = map_user_level(level, sourse='coursera')

    driver.get(f'https://www.coursera.org/search?query={skill}')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'main')))
    try:
        element = wait.until(EC.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div/main/div[2]/div/div[1]/div[2]/div/div/div/div/div/ul')))
        html_1 = driver.find_element_by_xpath('/html/body/div[2]/div/main/div[2]/div/div[1]/div[2]/div/div/div/div/div/ul').get_attribute('innerHTML')
    except:
        try:
            element = wait.until(EC.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div/main/div[2]/div/div[1]/div/div/div/div/div/div/ul')))
            html_1 = driver.find_element_by_xpath('/html/body/div[2]/div/main/div[2]/div/div[1]/div/div/div/div/div/div/ul').get_attribute('innerHTML')
        except:
            return []
    courses = ['https://www.coursera.org'+x for x in re.findall('data-track-href="(.+?)"', re.findall('<li class="ais-InfiniteHits-item"><div>(.+)', html_1)[0]) if 'search?' not in x]
    for course in courses:
        driver.get(course)
        html_coursera = driver.page_source
        if [x for x in re.findall('<div class="_1tu07i3a">(.+?)</div></div></div></div>', html_coursera) if f'{level} уровень' in x]:
            tags = re.findall('<span class="_1q9sh65">(.+?)</span>', re.findall('<div class="Skills(.+?)</span></div></div>', html_coursera)[0])
            if re.findall('<h1 class="banner-title banner-title-without--subtitle m-b-0" data-e2e="xdp-banner-title">(.+?)</h1>', html_coursera):
                name = re.findall('<h1 class="banner-title banner-title-without--subtitle m-b-0" data-e2e="xdp-banner-title">(.+?)</h1>', html_coursera)[0]
            elif re.findall('<h1 class="banner-title m-b-0" data-e2e="xdp-banner-title">(.+?)</h1>', html_coursera):
                name = re.findall('<h1 class="banner-title m-b-0" data-e2e="xdp-banner-title">(.+?)</h1>', html_coursera)[0]
            result[name]['link'] = course
            result[name]['tags'] = tags
    return result


def get_all_courses(skill, level, matrix):
    result = get_courses_harvard(skill, level, matrix)
    result.update(get_coursera_courses(skill, level))
    return result


def offer_courses():
    matrix = build_skills_matrix()

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    skills_ID = list(cur.execute("SELECT SkillID FROM Needed_Skills ORDER BY Gap"))
    for skill in skills_ID:

        cur.execute("SELECT Skill_Name FROM Skill WHERE SkillID =?", skill)
        skill_name = cur.fetchone()
        cur.execute("SELECT UserPoints FROM Needed_Skills WHERE SkillID =?", skill)
        point = cur.fetchone()

        courses = get_all_courses(skill_name[0], point[0], matrix)

        if len(courses) == 0:
            print(f'Релевантных курсов для навыка {skill_name[0]} пока не найдено')
        else:
            course_titles = list(courses.keys())
            course_title = course_titles[0]  # пока предлагаем только 1 курс с сайта
            print(f'Чтобы развить навык {skill_name[0]},'
                  f" попробуйте пройти курс {course_title}, ссылка на курс: {courses[course_title]['link']}")
