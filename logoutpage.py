from nicegui import app,ui
import user
from utility import logNavigate
import dbutils

@ui.page('/logout/')
def page_logout():
    user.UserCollection.logout(app.storage.user.get('username', ''))
    app.storage.user.update({'authenticated': False})
#    dbutils.taskDB.close_connection()
    logNavigate('/login/')
