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
    saveData(postJson)
    for element in postJson['hello']:
        print(element)
    print(round_time_object(datetime.now()))
    return 'received request'

def saveData(obj):
    with open('./data/temp.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def openData():
    with open('./data/temp.pkl', 'rb') as f:
        return pickle.load(f)

def round_time_object(timeObject):
    newTimeObject = datetime(timeObject.year, timeObject.month, timeObject.hour, round(60 / int(timeObject.minute)))
    return newTimeObject