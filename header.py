from nicegui import app,ui
from utility import sync_db, logNavigate

def logout() -> None:
    sync_db()
    logNavigate('/logout/')

def gotoReports() -> None:
    sync_db()
    logNavigate('/repoframe/')

def gotoKanban() -> None:
    logNavigate('/kanban/')



def header():
    with ui.header().classes('bg-gray-100'):
        with ui.row().classes('w-full'):
            ui.image('static/logo.png').classes('w-12')
            ui.space()
            ui.label(f'Time Tracker').classes('text-slate-600 text-3xl font-[Roboto] font-bold')
            ui.space()
            with ui.button(on_click=gotoReports, icon='article').classes('w-12').props('outline round') as btn:
                ui.tooltip('Reports page')
                btn.set_visibility(app.storage.user.get('authenticated', False))
                if app.storage.user.get('path','')=='/repoframe/':
                    btn.set_visibility(False)
            with ui.button(on_click=sync_db, icon='sync').classes('w-12').props('outline round') as btn:
                ui.tooltip('Synchronize to the DB')
                btn.set_visibility(app.storage.user.get('authenticated', False))
                if app.storage.user.get('path','')=='/repoframe/':
                    btn.set_visibility(False)
            with ui.button(on_click=logout if app.storage.user.get('path', '') != '/repoframe/' else gotoKanban,
                            icon='logout').classes('w-12').props('outline round') as btn:
                ui.tooltip('Logout from the session')
                btn.set_visibility(app.storage.user.get('authenticated', False))


