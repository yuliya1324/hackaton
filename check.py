import sqlite3
import pandas as pd
from collections import defaultdict, Counter
import random


con = sqlite3.connect('tasks.db')
cur = con.cursor()


def get_graph():
    tag_query = """
    SELECT *
    FROM problem_tag 
    """
    cur.execute(tag_query)
    tags = cur.fetchall()
    graph = {}
    for tag in tags:
        if tag[0] not in graph:
            graph[tag[0]] = {'tags': set(), 'tasks': set()}
        graph[tag[0]]['tags'].add(tag[1])
        for node in graph:
            if tag[1] in graph[node]['tags'] and node != tag[0]:
                graph[node]['tasks'].add(tag[0])
                graph[tag[0]]['tasks'].add(node)
    return graph


def get_df():
    query = """
    SELECT *
    FROM problems
    """
    return pd.read_sql_query(query, con=con)


def check_task(inp, output):
    from test import task
    if task(inp) == output:
        return True
    else:
        return False


def give_task(data, solved, known, unknown, links, i, task):
    t = data[data['id_problem'] == task]
    tags = links[task]['tags']
    print(t['text'].values[0])
    ready = input('If you are ready print "ok": ')
    if ready == 'ok':
        solved.append(task)
        if check_task(t['input'].values[0], t['output'].values[0]):
            known.extend(tags)
            for tag in tags:
                if tag in unknown:
                    unknown.remove(tag)
        else:
            unknown.extend(tags)
    else:
        unknown.extend(tags)
    i += 1
    if i < 5:
        next_task = random.choice(list(links[task]['tasks']))
        while next_task in solved:
            next_task = random.choice(links[task]['tasks'])
        solved, known, unknown = give_task(data, solved, known, unknown, links, i, next_task)
        return solved, known, unknown
    else:
        return solved, known, unknown


def get_skills(ns):
    skill_query = """
        SELECT *
        FROM tags 
        """
    skills = pd.read_sql_query(skill_query, con=con)
    result = []
    for n in ns:
        result.append(skills[skills['id_tag'] == n]['name'].values[0])
    return result


skills_known = []
skills_unknown = []
solved_tasks = []
graph = get_graph()
df = get_df()
print('Сейчас вам будут предложены 5 задач, которые необходимо решить. '
      'Для этого в файле test.py нужно написать функцию, которая на вход принимает input и возвращает output')
solved_tasks, skills_known, skills_unknown = give_task(df, solved_tasks, skills_known, skills_unknown, graph,
                                                       0, df.sample()['id_problem'].values[0])
freq = Counter(skills_known)
skills_known = [x for x in freq if freq[x] > 1]
real_unknown = []
for skill in skills_unknown:
    if skill not in skills_known:
        real_unknown.append(skill)
to_learn = get_skills(set(real_unknown))
print(f'Подучите {", ".join(to_learn)}')

