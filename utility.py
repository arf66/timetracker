from nicegui import app,ui
import dbutils
from constants import DB_STATUSES
from tasks import _tasks
import datetime
import time
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
    today = datetime.datetime.today()
    # Format the date in the desired format
    return today.strftime("%Y-%m-%d")

def fromEpochToDatetime(epoch_time):
    # Convert epoch time to a datetime object
    dt = datetime.datetime.fromtimestamp(epoch_time)
    
    # Format the date and time
    date_string = dt.strftime("%Y-%m-%d")
    time_string = dt.strftime("%H:%M")
    
    # Return a tuple with the date and time
    return (date_string, time_string)

def daysDifference(due):
    # due comes as an epoch timestamp
    # calculate difference in days
    return int((due - time.time())/86400)

def secsToHHMM(seconds):
    # Create a timedelta object from the given number of seconds
    time_delta = datetime.timedelta(seconds=seconds)
    
    # Extract hours and minutes
    total_seconds = int(time_delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    
    # Format the result as a string in '%H:%M'
    return f"{hours:02}:{minutes:02}"

def getEpochRange(year: str, month: str):
    # Convert input strings to integers
    year = int(year)
    nummonth = 1 if len(month)==0 else int(month)
    
    # Create datetime objects for the start and end of the month
    start_date = datetime.datetime(year, nummonth, 1)
    
    # Compute the end of the month by moving to the next month and subtracting one day
    if nummonth == 12:
        # If it's December, move to January of the next year
        end_date = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        # Otherwise, move to the next month in the same year
        end_date = datetime.datetime(year, nummonth + 1, 1) - datetime.timedelta(days=1)

    # Convert datetime objects to epoch timestamps
    start_epoch = int(time.mktime(start_date.timetuple()))
    end_epoch = int(time.mktime(end_date.timetuple())) + 86399  # Add seconds for the full last day

    return start_epoch, end_epoch


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
    
if __name__ in {'__main__', '__mp_main__'}:
    (f,t)=getEpochRange('2024', '01')
    print(f'Epochs {f} and {t}')
    ft=fromEpochToDatetime(f)
    tt=fromEpochToDatetime(t)
    print(f'From: {ft}')    
    print(f'To: {tt}')