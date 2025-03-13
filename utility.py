from nicegui import app,ui
import dbutils
from constants import DB_STATUSES
from tasks import _tasks
from datetime import datetime, timedelta
import pytz
from json import load
from uuid import uuid4
import dbutils


def protectPage(authenticated):
    return not authenticated

def checkpwd(user, pwd):
    return dbutils.userDB.check_user(user, pwd)

def logNavigate(path):
#    print(path)
    ui.navigate.to(path)

def setBackgroud():
        ui.query('body').classes(f"bg-[url(/static/background.jpg)] bg-cover")

def sync_db() -> None:
    dbutils.taskDB.delete_user_tasks(app.storage.user["username"])
    for s in DB_STATUSES:
        for el in _tasks[app.storage.user["username"]][s]:
            if el['user']==app.storage.user["username"]:
                dbutils.taskDB.create_task(el['id'], el['user'], el['title'], el['tag'], el['customer'], el['created'], s, 
                    el['due_time'], el['begin_time'], el['last_begin_time'], el['end_time'], el['duration'])
    ui.notify('DB synced')

def getEpochFromDateTime(date_string, timezone_str=None):

    # Handle the empty string
    if len(date_string)==0:
        return 0.0

    # Get the timezone from the local cookie
    if timezone_str==None:
        timezone_str=app.storage.user["defaulttz"]

    # Define the format of the input string
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create a naive datetime object from the input string
    naive_dt = datetime.strptime(date_string, date_format)
    
    # Localize the naive datetime object to the specified timezone
    timezone = pytz.timezone(timezone_str)
    localized_dt = timezone.localize(naive_dt)
    
    # Convert the localized datetime object to a timestamp (epoch)
    return float(localized_dt.timestamp())

def getToday():
    # Get the current date
    today = datetime.today()
    # Format the date in the desired format
    return today.strftime("%Y-%m-%d")

def fromEpochToDatetime(epoch_time):
    # Convert epoch time to a datetime object
    dt = datetime.fromtimestamp(epoch_time)
    
    # Format the date and time
    date_string = dt.strftime("%Y-%m-%d")
    time_string = dt.strftime("%H:%M")
    
    # Return a tuple with the date and time
    return (date_string, time_string)

def secsToHHMM(seconds):
    # Create a timedelta object from the given number of seconds
    time_delta = timedelta(seconds=seconds)
    
    # Extract hours and minutes
    total_seconds = int(time_delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    
    # Format the result as a string in '%H:%M'
    return f"{hours:02}:{minutes:02}"

def loadFromFile(user, file, tz):
    # load the data from the file
    try:
        with open(file, "r") as f:
            jsondata = load(f)
    except:
        print(f'Error while reading data from {file}')
        return
    # process data insertions
    ix=0
    for el in jsondata.keys():
        ix += 1
        record=jsondata[el]
        creation_date=getEpochFromDateTime(record['Creation_Date'], tz)
        due_date=getEpochFromDateTime(record['Due_Date'], tz)
        begin_time=getEpochFromDateTime(record['Begin_Time'], tz)
        complete_time=getEpochFromDateTime(record['Complete_Time'], tz)
        last_begin_time=getEpochFromDateTime(record.get('Last_Begin_Time',''), tz)
        retval = dbutils.taskDB.create_task(uuid4().urn, user, record['Title'], record['Tag'], 
            record['Customer'], creation_date, record['Status'], 
            due_date, begin_time, last_begin_time, complete_time, record['Duration']*60)
        if not retval:
            print(f"Error at key {el}")
            return ix
    return ix
    
    
