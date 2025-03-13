from constants import STATUSES
from copy import deepcopy
from time import time
import dbutils

_tasks={}

def addTask(user, id, tit, tag, cust, stat, due_time, 
            created=None, begin_time=None, last_begin_time=None, end_time=None, duration=None):
    if created is None:
        # Called from the kanban page
        _tasks[user][stat].append({
                             'user': user,
                             'id': id, 
                             'title': tit, 
                             'tag': tag, 
                             'customer': cust, 
                             'created': time(),
                             'due_time': due_time,
                             'begin_time': 0.0,
                             'last_begin_time': 0.0,
                             'end_time': 0.0,
                             'duration': 0.0
                             })
    else:
        # Called during _tasks initialization
        _tasks[user][stat].append({
                             'user': user,
                             'id': id, 
                             'title': tit, 
                             'tag': tag, 
                             'customer': cust, 
                             'created': created,
                             'due_time': due_time,
                             'begin_time': begin_time,
                             'last_begin_time': last_begin_time,
                             'end_time': end_time,
                             'duration': duration
                             })

def initTasks(user):
    if user not in _tasks:
        _tasks[user]={}

    for el in STATUSES:
        _tasks[user][el]=[]
    retval = dbutils.taskDB.read_all_tasks(user)
    for el in retval:
        addTask(el[1], el[0], el[2], el[3], el[4], el[6], el[5], el[7], el[8], el[9], el[10], el[11])

def removeTask(user, id):
    for s in STATUSES:
        for el in _tasks[user][s]:
            if el['id']==id:
                _tasks[s].remove(el)

def moveTask(user, id, stat):
    for s in STATUSES:
        for el in _tasks[user][s]:
            if el['id']==id:
                # If there's no change do nothing
                if s==stat:
                    return
                newel=deepcopy(el)
                # implement time calculation login
                # 1) task is starting or restarting
                if s=='Ready' and stat=='Doing':
                    if newel['begin_time'] == 0.0:
                        newel['begin_time']=time()
                    newel['last_begin_time']=time()
                # 2) task is ending
                if  stat=='Done':
                    newel['end_time']=time()
                    newel['duration']+=(newel['end_time']-newel['last_begin_time'])
                # 3) task is back to ready
                if  stat=='Ready':
                    if newel['last_begin_time'] != 0.0:
                        newel['duration']+=(time()-newel['last_begin_time'])
                _tasks[user][s].remove(el)
                _tasks[user][stat].append(newel)
                return


def findTask(user, id):
    for s in STATUSES:
        for el in _tasks[user][s]:
            if el['id']==id:
                return el
    return None

def printTasks(user):
    for stat in STATUSES:
        print('*'*20, stat, '*'*20)
        for el in _tasks[user][stat]:
            if el['user']==user:
                for k in el.keys():
                    print(f'{k}, {el[k]}\t', end='')
                print()
        print('*'*50)
        print()