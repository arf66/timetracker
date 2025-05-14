from nicegui import app, ui
import argparse
from utility import protectPage, logNavigate, loadFromFile
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

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='')
    parser.add_argument('--load', default='')
    parser.add_argument('--tz', default='')
    args=parser.parse_args()
    if args.user != '' and args.load != '':
        if args.tz=='':
            tz='CET'
        else:
            tz = args.tz
        print(f'Loading data for user {args.user} from file {args.load}')
        dbutils.taskDB = dbutils.Tasks(db_name=DATABASE, user=args.user)
        retval = loadFromFile(args.user, args.load, tz)
        print(f'Added {retval} records to user {args.user} database')
    else:
        create()
        app.add_static_files('/static', 'static')
        user.UserCollection=user.UserManager()
        dbutils.userDB = dbutils.TrelloDatabase(DATABASE)
        ui.run(port=8011, storage_secret='!A1w2e3r4', reload=False, title='Time Tracker', favicon="static/logo.png")