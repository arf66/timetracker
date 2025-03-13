from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage, fromEpochToDatetime, secsToHHMM
from header import header
from footer import footer
from tasks import findTask
 
@ui.page('/details/')
def details_page(id: str):

    fields=[]
    btnEdit={'ui': None, 'mode': 'Edit'}
    
    def editViewMode():
        for el in fields:
            if btnEdit['mode']=='Edit':
                el.enabled=True
            else:
                el.enabled=False
        if btnEdit['mode'] == 'Edit':
            btnEdit['mode']='View'
        else:
            btnEdit['mode']='Edit'
        btnEdit['ui'].text=btnEdit['mode']
    
    def cardField(t, v, type='Input'):
        if type=='Input':
            with ui.row().classes('w-full items-baseline'):
                ui.label(t)
                ui.space()
                retval =ui.input(value=v).classes('w-64')
                retval.enabled=False
                return retval
        elif type=='DateTime':
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



    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return

    if id[:8]=='urn:uuid:':
        id=id[8:]
    task = findTask(id)
    if  task is None:
        logNavigate('/kanban/')
    setBackgroud()
    header()
    with ui.card().classes('w-4/12 h-11/12 absolute-center') as c:
        fields.append(cardField('Title', task['title']))
        fields.append(cardField('Tag', task['tag']))
        fields.append(cardField('Customer', task['customer']))
        (d,t)=cardField('Begin Time', task['begin_time'], 'DateTime')
        fields.append(d)
        fields.append(t)
        (d,t)=cardField('Last Begin Time', task['last_begin_time'], 'DateTime')
        fields.append(d)
        fields.append(t)
        (d,t)=cardField('End Time', task['end_time'], 'DateTime')
        fields.append(d)
        fields.append(t)
        fields.append(cardField('Duration', task['duration'], 'Duration'))

        with ui.row().classes('w-full'):
            ui.button('Cancel', on_click=lambda: logNavigate('/kanban/')).props('flat')
            ui.space()
            btnEdit['ui']=ui.button(btnEdit['mode'], on_click=lambda: editViewMode()).props('flat')
    footer()