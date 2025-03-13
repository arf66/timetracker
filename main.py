from nicegui import app, ui
from utility import protectPage, logNavigate
from allpages import create
import user
import dbutils
from constants import DATABASE

@ui.page('/')
def page_root():
    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
    else:
        logNavigate('/kanban/')

if __name__ in {'__main__', '__mp_main__'}:
    create()
    app.add_static_files('/static', 'static')
    user.UserCollection=user.UserManager()
    dbutils.userDB = dbutils.TrelloDatabase(DATABASE)
    ui.run(port=8011, storage_secret='!A1w2e3r4')