from nicegui import app,ui
from utility import sync_db, logNavigate
from constants import ADMIN_ROLE

def logout() -> None:
    sync_db()
    logNavigate('/logout/')

def gotoReports(dest) -> None:
    sync_db()
    logNavigate(dest)

def gotoKanban() -> None:
    logNavigate('/kanban/')



def header():
    with ui.header().classes('bg-gray-100'):
        with ui.row().classes('w-full'):
            ui.image('static/logo.png').classes('w-12')
            ui.space()
            ui.label(f'Time Tracker').classes('text-slate-600 text-3xl font-[Roboto] font-bold')
            ui.space()
            if app.storage.user.get('role')==ADMIN_ROLE:
                with ui.button(on_click=lambda: logNavigate('/usermgr/'), icon='manage_accounts', color='red').classes('w-12').props('outline round') as usrbtn:
                    ui.tooltip('User Management')
                    usrbtn.set_visibility(app.storage.user.get('authenticated', False))
                    if app.storage.user.get('path','') in ['/repoadmin/', '/repoframe/', '/usermgr/']:
                        usrbtn.set_visibility(False)
                with ui.button(on_click=lambda: gotoReports('/repoadmin/'), icon='article', color='red').classes('w-12').props('outline round') as admbtn:
                    ui.tooltip('Admin Reports')
                    admbtn.set_visibility(app.storage.user.get('authenticated', False))
                    if app.storage.user.get('path','') in ['/repoadmin/', '/repoframe/', '/usermgr/']:
                        admbtn.set_visibility(False)
            with ui.button(on_click=lambda: gotoReports('/repoframe/'), icon='article').classes('w-12').props('outline round') as btn:
                ui.tooltip('Reports page')
                btn.set_visibility(app.storage.user.get('authenticated', False))
                if app.storage.user.get('path','') in ['/repoadmin/', '/repoframe/', '/usermgr/']:
                    btn.set_visibility(False)
            with ui.button(on_click=sync_db, icon='sync').classes('w-12').props('outline round') as btn:
                ui.tooltip('Synchronize to the DB')
                btn.set_visibility(app.storage.user.get('authenticated', False))
                if app.storage.user.get('path','') in ['/repoadmin/', '/repoframe/', '/usermgr/']:
                    btn.set_visibility(False)
            with ui.button(on_click=logout if app.storage.user.get('path', '') not in ['/repoadmin/', '/repoframe/', '/usermgr/'] else gotoKanban,
                            icon='logout').classes('w-12').props('outline round') as btn:
                ui.tooltip('Logout from the session')
                btn.set_visibility(app.storage.user.get('authenticated', False))


