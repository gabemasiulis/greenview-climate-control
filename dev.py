import pickle
from datetime import datetime, timedelta

def genSample():
    newDataDict = { "data": []}
    newData1 = {
        "name": "1 New",
        "data": {}
    }
    timestampNow = round_time_object(datetime.now())
    newData1['timestamp'] = timestampNow
    newDataDict['data'].append(newData1)
    newData2 = {
        "name": "2 New",
        "data": {}
    }
    newData2['timestamp'] = timestampNow
    newDataDict['data'].append(newData2)
    olderData1 = {
        "name": "1 Older",
        "data": {}
    }
    timestampOlder = round_time_object(datetime.now() - timedelta(hours=1))
    olderData1['timestamp'] = timestampOlder
    newDataDict['data'].append(olderData1)
    olderData2 = {
        "name": "2 Older",
        "data": {}
    }
    olderData2['timestamp'] = timestampOlder
    newDataDict['data'].append(olderData2)
    oldestData1 = {
        "name": "1 Oldest",
        "data": {}
    }
    timestampOldest = round_time_object(datetime.now() - timedelta(days=1))
    oldestData1['timestamp'] = timestampOldest
    newDataDict['data'].append(oldestData1)
    oldestData2 = {
        "name": "2 Oldest",
        "data": {}
    }
    oldestData2['timestamp'] = timestampOldest
    newDataDict['data'].append(oldestData2)
    print(newDataDict)
    saveData(newDataDict)

def round_time_object(timeObject):
    newMinutes = round(int(timeObject.minute) / 15) * 15
    newHours =int(timeObject.hour)
    if newMinutes == 60:
        newHours += 1
        newMinutes = 0
    newTimeObject = datetime(timeObject.year, timeObject.month, timeObject.day, newHours, newMinutes)
    return newTimeObject
def saveData(obj):
    with open('./data/temp.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)