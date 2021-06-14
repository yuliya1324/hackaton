import json
import os
import requests
import time
import shutil


def parse_vacancies(grade_occupation: str) -> None:
    """
    Парсит сайт с вакансиями.
    @param grade_occupation:  желаемая профессия
    """
    get_pages(grade_occupation)
    get_vacancies()


def get_page(grade_occupation: str, page: int = 0) -> str:
    """
    Метод для получения страницы со списком вакансий.
    @param grade_occupation:  желаемая профессия
    @param  page: индекс страницы, начинается с 0. Значение по умолчанию 0, т.е. первая страница
    """

    # Справочник для параметров GET-запроса
    params = {
        'text': f'NAME:{grade_occupation}',  # Текст фильтра. В имени должно быть слово "Аналитик"
        'area': 1,  # Поиск ощуществляется по вакансиям города Москва
        'page': page,  # Индекс страницы поиска на HH
        'per_page': 100  # Кол-во вакансий на 1 странице
    }

    req = requests.get('https://api.hh.ru/vacancies', params)
    data = req.content.decode()  # Декодируем, чтобы Кириллица отображалась корректно
    req.close()
    return data


def get_pages(grade_occupation: str) -> None:
    """
        Функция считывает и сохраняет в json поученные страницы с вакансиями
        @param grade_occupation:  желаемая профессия
    """

    if os.path.exists('./docs'):
        shutil.rmtree('./docs')  # удаляет папку вместе содержимым, если папка сушествует и создаём пустую
    os.makedirs('./docs')

    # Считываем первые 1000 вакансий
    for page in range(0, 10):

        # Преобразуем текст ответа запроса в справочник Python
        js_obj = json.loads(get_page(grade_occupation, page))

        # Определяем количество файлов в папке для сохранения документа с ответом запроса
        # Полученное значение используем для формирования имени документа

        next_file_name = f"./docs/{len(os.listdir('./docs'))}.json"

        # Создаем новый документ, записываем в него ответ запроса, после закрываем
        f = open(next_file_name, mode='w', encoding='utf8')
        f.write(json.dumps(js_obj, ensure_ascii=False))
        f.close()

        # Проверка на последнюю страницу, если вакансий меньше 2000
        if (js_obj['pages'] - page) <= 1:
            break

        # Задержка, чтобы не нагружать сервисы hh
        time.sleep(0.25)


def get_vacancies() -> None:
    """
        Функция считывает поученные страницы с вакансиями,
        далее сохраняет детальные даннные по каждой вакансии
    """

    if os.path.exists('./vacancies'):
        shutil.rmtree('./vacancies')  # удаляет папку вместе содержимым, если папка сушествует и создаём пустую
    os.makedirs('./vacancies')

    # Получаем перечень ранее созданных файлов со списком вакансий и проходимся по нему в цикле
    for fl in os.listdir('./docs'):

        # Открываем файл, читаем его содержимое, закрываем файл
        f = open('./docs/{}'.format(fl), encoding='utf8')
        json_text = f.read()
        f.close()

        # Преобразуем полученный текст в объект справочника
        json_obj = json.loads(json_text)

        # Получаем и проходимся по непосредственно списку вакансий
        for v in json_obj['items']:
            # Обращаемся к API и получаем детальную информацию по конкретной вакансии
            req = requests.get(v['url'])
            data = req.content.decode()
            req.close()

            # Создаем файл в формате json с идентификатором вакансии в качестве названия
            # Записываем в него ответ запроса и закрываем файл
            file_name = './vacancies/{}.json'.format(v['id'])
            f = open(file_name, mode='w', encoding='utf8')
            f.write(data)
            f.close()

            time.sleep(0.25)
