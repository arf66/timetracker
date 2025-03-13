#!/usr/bin/env python3
from dataclasses import dataclass
import draganddrop as dnd
from constants import STATUSES, TAGS, DATABASE
from nicegui import app,ui
from header import header
from footer import footer
import dbutils
import tasks
from uuid import uuid4
from utility import setBackgroud, getEpochFromDateTime, protectPage, logNavigate, getToday

@ui.page('/kanban/')
def kanban_page():
    @dataclass
    class ToDo:
        id: str
        title: str
        tag: str
        status: str
        customer: str
        duration: int

    containers=[]

    def findContainer(n):
        for i,e in enumerate(containers):
            if e.name==n:
                return i


    def clearFields(tit, tag, stat, cust, date):
        tit.value=''
        tag.value=''
        stat.value=''
        cust.value=''
        date.value=''

    def createTaskUI():
        for s in STATUSES:
            for el in tasks._tasks[s]:
                with containers[findContainer(s)]:
                    dnd.card(ToDo(el['id'], el['title'], el['tag'], s, el['customer'], el['duration']))
    
    def createTask(tit, tag, stat, cust, date):
        def checkField(f,t):
            if f.value is None or len(f.value)==0:
                ui.notify(t, type='warning')
                return False
            return True
        
        if not checkField(tit, 'Missing Title'):
            return
        if not checkField(tag, 'Missing Tag'):
            return
        if not checkField(cust, 'Missing Customer'):
            return
        if not checkField(stat, 'Missing Status'):
            return
        if not checkField(date, 'Missing Due Date'):
            return

        task_id=uuid4().urn
        due_time =  getEpochFromDateTime(date.value +" 23:59:59")
        tasks.addTask(app.storage.user["username"], task_id, tit.value, tag.value, cust.value, stat.value, due_time)

        with containers[findContainer(stat.value)]:
            dnd.card(ToDo(task_id, tit.value, tag.value, stat.value, cust.value, 0.0))
        clearFields(tit,tag, stat, cust, date)

    def handle_drop(todo: ToDo, location: str):
        ui.notify(f'"{todo.title}" is now in {location}')

    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return
    
    dbutils.taskDB = dbutils.Tasks(db_name=DATABASE, user=app.storage.user["username"])
    header()
    setBackgroud()

    with ui.splitter(horizontal=False, reverse=False, value=70).classes('w-full h-full') as splitter:
        with splitter.before:
            with ui.row().classes('w-full h-full'):
                for i,e in enumerate(STATUSES):
                    with dnd.column(e, on_drop=handle_drop) as el:
                        containers.append(el)
                    ui.space()             
        with splitter.after:
            with ui.card():
                with ui.column().classes('w-96 p-4 rounded shadow-2'):
                    titleField=ui.input(label='Title', placeholder='Title').classes('w-full')
                    tagField=ui.select(TAGS, label='Tag').classes('w-full').props('use-chips')
                    custField=ui.input(label='Customer', placeholder='Title').classes('w-full')
                    statusField=ui.select(STATUSES, label='Status').classes('w-full').props('use-chips')
                    with ui.input('Due Date', value=getToday()).classes('w-full') as date:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.date().bind_value(date):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                        with date.add_slot('append'):
                            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                    with ui.row().classes('w-full'):
                        ui.button('Clear', on_click= lambda: clearFields(titleField, tagField, statusField, custField, date)).props('flat')
                        ui.space()
                        ui.button('Debug', on_click= lambda: tasks.printTasks(app.storage.user["username"]))
                        ui.space()
                        ui.button('Create', on_click= lambda: createTask(titleField, tagField, statusField, custField, date)).props('flat')
        tasks.initTasks(app.storage.user["username"])
        createTaskUI()
    footer()


if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
