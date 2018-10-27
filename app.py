import atexit, pickle
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def job_function():
    data = openData()
    print(data)
scheduler.add_job(job_function, 'cron', second='*/15')
scheduler.start()
app = Flask(__name__)

atexit.register(lambda: scheduler.shutdown(wait=False))

@app.route('/', methods=['POST'])
def receive_post():
    if request.json is None:
        return "Please Submit JSON", 400
    postJson = request.json
    if 'name' not in postJson:
        return 'Must supply Sensor Name', 400
    newPost = {'name': postJson['name']}
    if 'data' not in postJson:
        return 'Must supply cllimate data', 400
    if 'temperature' not in postJson['data']:
        return 'Must supply temperature in data object', 400
    if 'humidity' not in postJson['data']:
        return 'Must supply humidity in data object', 400
    newData = {'temperature': postJson['data']['temperature'], 'humidity': postJson['data']['humidity']}
    newPost['data'] = newData
    updateData(newPost, openData())
    print(round_time_object(datetime.now()))
    return 'Created Entry', 201

def saveData(obj):
    with open('./data/temp.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def openData():
    with open('./data/temp.pkl', 'rb') as f:
        return pickle.load(f)

def updateData(newObj, data):
    print('updating data. Before:') 
    print(data)   
    timestampNow = round_time_object(datetime.now())
    '''
    Remove data entries that are greater than 24 hours
    '''
    newData = list(filter(lambda entry: (timestampNow - timedelta(days=1) < entry['timestamp']), data['data']))
    data['data'] = newData
    newObj['timestamp'] = timestampNow
    data['data'].append(newObj)
    print('after:')
    print(data)
    with open('./data/temp.pkl', 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    

def round_time_object(timeObject):
    newMinutes = round(int(timeObject.minute) / 15) * 15
    newHours =int(timeObject.hour)
    if newMinutes == 60:
        newHours += 1
        newMinutes = 0
    newTimeObject = datetime(timeObject.year, timeObject.month, timeObject.day, newHours, newMinutes)
    return newTimeObject