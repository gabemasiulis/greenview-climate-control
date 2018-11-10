import atexit, pickle, json, requests
from pathlib import Path
from wtforms import Form, StringField, validators
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def load_configuration():
    with open('config.json') as configJson:
        config = json.load(configJson)
        configJson.close()
        return config

def job_function():
    data = openData()
    print(data)
scheduler.add_job(job_function, 'cron', hour='*/20') # TODO change to a sane value 
scheduler.start()
app = Flask(__name__)
app.secret_key = load_configuration()['flask-secret-key']

atexit.register(lambda: scheduler.shutdown(wait=False))

class AuthorizationForm(Form):
    pin = StringField('Nest Pin', [validators.Length(min=8, max=8)])

@app.route('/authorize', methods=['GET', 'POST'])
def process_authorization_request():
    nestConfig = load_configuration()
    # testNestConnection(nestConfig) TODO finish this, if nest auth is good, redirect to another page
    authUrl = nestConfig['nest-authorization-url']
    form = AuthorizationForm(request.form)
    if request.method == 'POST' and form.validate():
        pin = form.pin.data
        print(pin)
        post_nest_authorization_request(pin, nestConfig) # TODO what happens next...
    return render_template('process_authorization_request.html', form=form, authUrl=authUrl)

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
    devices = getDevices()
    if postJson['name'] not in devices:
        addDevice(postJson['name'])
        return 'Submit data only from recognized devices', 400
    if devices[postJson['name']]['isRegistered'] == False:
        return 'Submit data only from registered devices', 400
    newData = {'temperature': postJson['data']['temperature']}
    if 'humidity' in postJson['data']:
        newData['humidity'] = postJson['data']['humidity']
        # TODO warn about missing humidity data
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
    filePath = Path('./data/devices.pkl')
    if Path(filePath).is_file == False:
        obj = {}
        with open(filePath, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    with open(filePath,'rb') as f:
        return pickle.load(f)

def saveData(obj):
    with open('./data/temp.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
def openData():
    filePath = './data/temp.pkl'
    if Path(filePath).is_file == False:
        import dev
        dev.genSample()
    with open(filePath, 'rb') as f:
        return pickle.load(f)

def updateData(newObj, data):
    print('updating data. Before:') 
    print(data)   
    timestampNow = round_time_object(datetime.now())
    
    ####################################################
    # Remove data entries that are greater than 96 hours
    ####################################################
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

def post_nest_authorization_request(pin, nestConfig):
    nestTokenUrl = 'https://api.home.nest.com/oauth2/access_token'
    payload = {
        'client_id': nestConfig['nest-client-id'],
        'client_secret': nestConfig['nest-client-secret'],
        'grant_type': 'authorization_code',
        'code': pin
    }
    r = requests.post(nestTokenUrl, data=payload)
    print(r.encoding)
    print(r.text)
    if r.status_code == 400:
        flash('Nest Token Generation Error: ' + json.loads(r.text)['error_description'])
        return 'Nest Token Generation Error: ' + json.loads(r.text)['error_description']
    flash('Authorized!')
    

def testNestConnection(nestConfig):
    clientId = nestConfig['nest-client-id']
    clientSecret = ['nest-client-secret']