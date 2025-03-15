from nicegui import ui
from utility import sync_db, logNavigate

def logout() -> None:
    sync_db()
    logNavigate('/logout/')

def gotoReports() -> None:
    logNavigate('/repoframe/')


def header():
    with ui.header().classes('bg-gray-100'):
        with ui.row().classes('w-full'):
            ui.image('static/logo.png').classes('w-12')
            ui.space()
            ui.label(f'Time Tracker').classes('text-slate-600 text-3xl font-[Roboto] font-bold')
            ui.space()
            with ui.button(on_click=gotoReports, icon='article').classes('w-12').props('outline round'):
                ui.tooltip('Reports page')
            with ui.button(on_click=sync_db, icon='sync').classes('w-12').props('outline round'):
                ui.tooltip('Synchronize to the DB')
            with ui.button(on_click=logout, icon='logout').classes('w-12').props('outline round'):
                ui.tooltip('Logout from the session')
