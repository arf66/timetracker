from nicegui import app, ui
from constants import VERSION



def footer():
    with ui.footer().classes('bg-gray-100'):
        with ui.row().classes('w-full'):
            if app.storage.user.get("username",'') != '' and app.storage.user.get("authenticated",False):
                ui.label(f'User: {app.storage.user.get("username",'')}').classes('text-slate-600 text-md')
            else:
                ui.label(f'').classes('text-slate-600 text-md')
            ui.space()
            ui.label(f'Version: {VERSION}').classes('text-slate-600 text-md')
