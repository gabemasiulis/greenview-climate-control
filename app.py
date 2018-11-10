import atexit, pickle
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def job_function():
    data = openData()
    print(data)
scheduler.add_job(job_function, 'cron', second='*/30')
scheduler.start()
app = Flask(__name__)

atexit.register(lambda: scheduler.shutdown(wait=False))

@app.route('/delete/')
@app.route('/delete/<index>')
def delete(index=None):
    if index == None:
        return redirect(url_for('welcome'))
    data = openData()
    del data['data'][int(index)]
    saveData(data)
    return redirect(url_for('welcome'))

@app.route('/', methods=['GET'])
def welcome():
    data = openData()
    return render_template('welcome.html', data=data['data'])

@app.route('/', methods=['POST'])
def receive_post():
    print(request.headers)
    if request.json is None:
        return "Please Submit JSON", 400
    postJson = request.json
    if 'name' not in postJson:
        return 'Must supply Sensor Name', 400
    newPost = {'name': postJson['name']}
    if 'data' not in postJson:
        return 'Must supply climate data', 400
    if 'temperature' not in postJson['data']:
        return 'Must supply temperature in data object', 400
    # if 'humidity' not in postJson['data']:
    #     return 'Must supply humidity in data object', 400
    devices = getDevices()
    if postJson['name'] not in devices:
        addDevice(postJson['name'])
        return 'Submit data only from recognized devices', 400
    if devices[postJson['name']]['isRegistered'] == False:
        return 'Submit data only from registered devices', 400
    newData = {'temperature': postJson['data']['temperature']}
    if 'humidity' in postJson['data']:
        newData['humidity'] = postJson['data']['humidity']
    newPost['data'] = newData
    updateData(newPost, openData())
    print(round_time_object(datetime.now()))
    return 'Created Entry', 201

@app.route('/devices/', methods=['GET'])
def manageDevices():
    devices = getDevices()
    return render_template('devices.html', devices=devices)

@app.route('/devices/', methods=['PATCH'])
def updateDevice():
    if request.json is None:
        return "Please Submit JSON", 400
    devices = getDevices()
    patchJson = request.json
    if 'deviceName' not in patchJson:
        return 'Must Supply Device Name', 400
    deviceName = patchJson['deviceName']
    if deviceName not in devices:
        return 'Must Supply a Pre-Existing Device', 400
    if 'field' not in patchJson:
        return 'Must Supply a Field to Update', 400
    if 'value' not in patchJson:
        return 'Must Supply a Value to Update', 400
    if patchJson['field'] == 'displayName':
        if type(patchJson['value']) != str:
            return 'Incorrect value type', 400
        devices[deviceName]['displayName'] = patchJson['value']
        with open('./data/devices.pkl', 'wb') as f:
            pickle.dump(devices, f, pickle.HIGHEST_PROTOCOL)
            return 'Record Updated', 200
    if patchJson['field'] == 'isRegistered':
        if type(patchJson['value']) != bool:
            return 'Incorrect value type', 400
        devices[deviceName]['isRegistered'] = patchJson['value']
        with open('./data/devices.pkl', 'wb') as f:
            pickle.dump(devices, f, pickle.HIGHEST_PROTOCOL)
            return 'Record Updated', 200
    return 'Must Supply an Existing Field to Update', 400

def addDevice(name):
    devices = getDevices()
    devices[name] = {
        'displayName': name,
        'isRegistered': False
    }
    with open('./data/devices.pkl', 'wb') as f:
        pickle.dump(devices, f, pickle.HIGHEST_PROTOCOL)
def getDevices():
    with open('./data/devices.pkl','rb') as f:
        return pickle.load(f)

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
    Remove data entries that are greater than 96 hours
    '''
    newData = list(filter(lambda entry: (timestampNow - timedelta(days=4) < entry['timestamp']), data['data']))
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

