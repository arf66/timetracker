from nicegui import ui
from utility import logNavigate, setBackgroud
import dbutils
import pytz

# Get the list of all available timezones
timezones = pytz.all_timezones

def try_saveuser(usr, pwd, role, utz):

    def checkField(f,t):
        if f.value is None or len(f.value)==0:
            ui.notify(t, type='warning')
            return False
        return True
        
    if not checkField(usr, 'Missing Username'):
        return
    if not checkField(pwd, 'Missing Password'):
        return
    if not checkField(role, 'Missing Role'):
        return
    if not checkField(utz, 'Missing User Timezone'):
        return

    if not dbutils.userDB.create_user(usr.value, pwd.value, role.value, utz.value):
        ui.notify('User already exist', color='negative')
    else:
        logNavigate('/login/')

@ui.page('/signup/')
def signup_page():
    roles=['','User', 'Reports']
    availtz=['']
    for el in timezones:
        availtz.append(el)

    setBackgroud()
    with ui.card().classes('size-96 absolute-center'):
        username = ui.input('Username').classes('w-full')
        password = ui.input('Password', password=True, password_toggle_button=True).classes('w-full')
        role = ui.select( roles, label='Role',value='').classes('w-full')
        usertz = ui.select( availtz, label='Timezone',value='').classes('w-full')
        ui.space()
        with ui.row().classes('w-full'):
            ui.button('Cancel', on_click=lambda: logNavigate('/login/')).props('flat')
            ui.space()
            ui.button('Create', on_click=lambda: try_saveuser(username, password, role, usertz)).props('flat')
