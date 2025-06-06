from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage
from header import header
from footer import footer
import dbutils
from constants import DEFAULT_ROLE, DEFAULT_TZ

columns = [
    {'field': 'id', 'minWidth': 30, 'maxWidth': 70},
    {'field': 'Username', 'editable': True, 'sortable': True, 'minWidth': 70, 'maxWidth': 200 },
    {'field': 'password', 'editable': False, 'minWidth': 70, 'maxWidth': 200},
    {'field': 'role', 'editable': True, 'sortable': True, 'minWidth': 70, 'maxWidth': 200},
    {'field': 'tz', 'editable': True, 'sortable': True, 'minWidth': 70, 'maxWidth': 200},
]

@ui.page('/usermgr/')
def usermgr_page():
    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return
    
    dbdata = dbutils.userDB.read_all_users()
    rows= [{'id': idx, 'Username': user[0], 'password': user[1], 'role': user[2], 'tz': user[3]} for idx, user in enumerate(dbdata)]
    header()
    setBackgroud()

    def add_row():
        new_id = max((dx['id'] for dx in rows), default=-1) + 1
        rows.append({'id': new_id, 'Username': f'New user {new_id}', 'password': 'NewPassword', 'role': DEFAULT_ROLE, 'tz': DEFAULT_TZ})
        dbutils.userDB.create_user( f'New user {new_id}', 'NewPassword', DEFAULT_ROLE, DEFAULT_TZ)
        ui.notify(f'Added row with ID {new_id}')
        aggrid.update()

    def handle_cell_value_change(e):
        new_row = e.args['data']
        old_user=''
        for row in rows:
            if row['id'] == new_row['id']:
                old_user = row['Username']
                break
        dbutils.userDB.delete_user( old_user)
        dbutils.userDB.create_user( new_row['Username'], new_row['password'], new_row['role'], new_row['tz'])
        rows[:] = [row | new_row if row['id'] == new_row['id'] else row for row in rows]
        ui.notify(f'Updated row to: {e.args["data"]}')

    async def delete_selected():
        selected_id = [row['id'] for row in await aggrid.get_selected_rows()]
        selected_usernames = [row['Username'] for row in rows if row['id'] in selected_id]
        rows[:] = [row for row in rows if row['id'] not in selected_id]
        for username in selected_usernames:
            dbutils.userDB.delete_user( username)
        ui.notify(f'Deleted row with ID {selected_id}')
        aggrid.update()

    aggrid = ui.aggrid({
        'columnDefs': columns,
        'rowData': rows,
        'rowSelection': 'multiple',
        'stopEditingWhenCellsLoseFocus': True,
    }).on('cellValueChanged', handle_cell_value_change)
    aggrid.style('width: calc(30%);')

    ui.button('Delete selected', on_click=delete_selected)
    ui.button('New row', on_click=add_row)

    footer()