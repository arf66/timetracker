from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage, \
    fromEpochToDatetime, secsToHHMM, getEpochFromDateTime
from header import header
from footer import footer
import dbutils
from constants import DATABASE
from tasks import findTask, _tasks
from customers import CustomersManager
 
@ui.page('/details/')
def details_page(id: str):

    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return

    if id[:8]=='urn:uuid:':
        id=id[8:]
    retval = findTask(app.storage.user['username'], id)
    if  retval is None:
        logNavigate('/kanban/')
    else:
        (taskstatus, task)=retval
    fields={}
    btnEdit={'ui': None, 'mode': 'Edit'}
    custlist=CustomersManager()
    custlist.load(app.storage.user["username"], _tasks)
    dbutils.taskDB = dbutils.Tasks(db_name=DATABASE, user=app.storage.user["username"])

    
    def fromControlToValue(date, time):
        if date != '' and time != '':
            return getEpochFromDateTime(f'{date} {time}:00')
        else:
            return 0.0

    def editViewMode():
        # prima abilito tutti i campi
        for el in fields.keys():
            fields[el].enabled=btnEdit['mode']=='Edit'

        if btnEdit['mode']=='Save':
            #raccolgo i dati dalla form
            due_time = getEpochFromDateTime(f'{fields['due_date'].value} 23:59:59')
            begin_time = fromControlToValue(fields['begin_date'].value, fields['begin_time'].value)
            last_begin_time = fromControlToValue(fields['last_begin_date'].value, fields['last_begin_time'].value)
            end_time = fromControlToValue(fields['end_date'].value, fields['end_time'].value)
            durstr= fields['duration'].value
            duration=float(durstr[0:2])*60+float(durstr[3:2])
            
            # poi salvo i dati sul db
            
            # dbutils.taskDB.update_task(id, fields['title'].value, fields['tag'].value, 
            #            fields['customer'].value, due_time, begin_time, 
            #            last_begin_time, end_time, duration)
            dbutils.taskDB.delete_task(id)
            dbutils.taskDB.create_task(id, app.storage.user['username'], fields['title'].value, fields['tag'].value, 
                        fields['customer'].value, task['created'], taskstatus, due_time,  begin_time, 
                        last_begin_time, end_time, duration)


        # poi rimetto a posto il bottone
        btnEdit['mode'] = 'Save' if btnEdit['mode']=='Edit' else 'Edit'
        btnEdit['ui'].text=btnEdit['mode']
    
    def cardField(t, v, type='Input', options=None):
        if type=='Input':
            with ui.row().classes('w-full items-baseline'):
                ui.label(t)
                ui.space()
                if options is not None:
                    retval =ui.input(value=v, autocomplete=options).classes('w-64')
                else:
                    retval =ui.input(value=v).classes('w-64')
                retval.enabled=False
                return retval
        elif type in ['DateTime','Date']:
            if v==0:
                date_value=''
                time_value=''
            else:
                (date_value, time_value)=fromEpochToDatetime(v)
                
            with ui.row().classes('w-full items-baseline'):
                ui.label(t)
                ui.space()
                with ui.input(t, value=date_value).classes('w-32') as retval:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(retval):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                with retval.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
                retval.enabled=False

                retval2=None
                if type=='DateTime':
                    with ui.input(t, value=time_value).classes('w-32') as retval2:
                        with ui.menu().props('no-parent-event') as menu:
                            with ui.time().bind_value(retval2):
                                with ui.row().classes('justify-end'):
                                    ui.button('Close', on_click=menu.close).props('flat')
                    with retval2.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
                    retval2.enabled=False                
            return (retval, retval2)
        else:
            time_value=secsToHHMM(v)
            with ui.row().classes('w-full items-baseline'):
                ui.label(t)
                ui.space()
                retval =ui.input(value=time_value).classes('w-64')
                retval.enabled=False
            return retval

    def exitDetails():
        logNavigate('/kanban/')

    setBackgroud()
    header()
    with ui.card().classes('w-4/12 h-11/12 absolute-center') as c:
        fields['title']=cardField('Title', task['title'], type='Input')
        fields['tag']=cardField('Tag', task['tag'], type='Input')
        fields['customer']=cardField('Customer', task['customer'], type='Input', 
                                             options=custlist.get_all())
        (d,t)=cardField('Due Date', task['due_time'], type='Date')
        fields['due_date'] = d
        (d,t)=cardField('Begin Time', task['begin_time'], type='DateTime')
        fields['begin_date'] = d
        fields['begin_time'] = t
        (d,t)=cardField('Last Begin Time', task['last_begin_time'], type='DateTime')
        fields['last_begin_date'] = d
        fields['last_begin_time'] = t
        (d,t)=cardField('End Time', task['end_time'], type='DateTime')
        fields['end_date'] = d
        fields['end_time'] = t
        fields['duration'] = cardField('Duration', task['duration'], type='Duration')

        with ui.row().classes('w-full'):
            ui.button('Cancel', on_click=lambda: exitDetails()).props('flat')
            ui.space()
            btnEdit['ui']=ui.button(btnEdit['mode'], on_click=lambda: editViewMode()).props('flat')
            btnEdit['ui'].enabled=(taskstatus!='Done')
    footer()