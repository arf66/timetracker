from nicegui import app, ui
from utility import checkpwd, logNavigate, setBackgroud
import user
import dbutils
from header import header
from footer import footer

@ui.page('/login/')
def login_page():

    def sign_up():
        logNavigate('/signup/')

    def try_login():  
        if checkpwd(username.value, password.value):
            userdata = dbutils.userDB.get_user(username.value)
            defaulttz=userdata[3]
            userrole=userdata[2]
            if not user.UserCollection.user_exists(username.value):
                user.UserCollection.create_user(username.value, '')
            user.UserCollection.login(username.value)
            app.storage.user.update({'username': username.value, 'defaulttz': defaulttz, 'role': userrole, 'authenticated': True})
        else:
            ui.notify('Wrong username or password', color='negative')
        if app.storage.user.get('authenticated', False):
            logNavigate('/kanban/')

    setBackgroud()
    header()
    if app.storage.user.get('authenticated', False):
        username =app.storage.user.get('username', '')
        if not user.UserCollection.user_exists(username):
            user.UserCollection.create_user(username, '')
        user.UserCollection.login(username)
        logNavigate('/kanban/')
    with ui.card().classes('size-64 absolute-center'):
        ui.space()
        username = ui.input('Username').on('keydown.enter', try_login).classes('w-full')
        ui.space()
        password = ui.input('Password', password=True).on('keydown.enter', try_login).classes('w-full')
        ui.space()
        with ui.row().classes('w-full'):
            ui.button('Sign in', on_click=try_login).props('flat')
            ui.space()
            ui.button('Sign up', on_click=sign_up).props('flat')
    footer()
        
