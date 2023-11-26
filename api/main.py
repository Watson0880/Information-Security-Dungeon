from flask import Flask, render_template
from flask import request
from flask import Response
from flask_cors import CORS
import os
import json
from pymongo.mongo_client import MongoClient

class Record:
    def __init__(self,uid,usingtime,wrongtime,uploadtime):
        self.uid = uid
        self.usingtime = usingtime
        self.wrongtime = wrongtime
        self.uploadtime = uploadtime

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/rank')
def getrank():
    return render_template('/rank.html')

@app.route('/uploadrecord',methods=["POST"])
def uploadrecord():
    data = request.get_data()
    data = json.loads(data)
    uid = str(data["uid"])
    usingtime = str(data["usingtime"])
    wrongtime = str(data["wrongtime"])
    uploadtime = str(data["uploadtime"])
    uri = os.environ.get('URL')
    db_name = "rank"
    collection_name = "record"
    client = MongoClient(uri)
    database = client[db_name]
    collection = database[collection_name]
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    collection.insert_one({'uid':uid,'usingtime':usingtime,'wrongtime':wrongtime,'uploadtime':uploadtime})
    print("insert one data")
    return render_template('/requeststatus.html',message="Success")
    '''
    try:
        pass
    except Exception as e:
        print(e)
        return render_template('/requeststatus.html',message="Fail")
    '''
@app.route('/getrecord',methods=["GET"])
def getrecord():
    uri = os.environ.get('URL')
    db_name = "rank"
    collection_name = "record"
    client = MongoClient(uri)
    database = client[db_name]
    collection = database[collection_name]
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    data = collection.find()
    records = []
    for i in data:
        records.append(Record(i['uid'],i['usingtime'],i['wrongtime'],i['uploadtime']))
    jsonlist = []
    if len(records)>100:
        for i in range(100):
            fast = Record(0,3600000*24,0,0)
            for j in records:
                jtime = int(j['usingtime'][0:2])*3600000 + int(j['usingtime'][3:5])*60000 + int(j['usingtime'][6:8])*1000 + int(j['usingtime'][9:12])
                fasttime = int(fast['usingtime'][0:2])*3600000 + int(fast['usingtime'][3:5])*60000 + int(fast['usingtime'][6:8])*1000 + int(fast['usingtime'][9:12])
                if jtime<fasttime:
                    fast = j
                elif jtime == fasttime:
                    if int(j[wrongtime])<int(fast[wrongtime]):
                        fast = j
                    elif int(j[wrongtime])==int(fast[wrongtime]):
                        pass #先不做
            #add to json
            jsonlist.append(fast)
            #remove from records
            records.remove(fast)
    else:
        for i in range(len(records)):
            fast = Record(0,3600*24,0,0)
            for j in records:
                jtime = int(j['usingtime'][0:2])*3600000 + int(j['usingtime'][3:5])*60000 + int(j['usingtime'][6:8])*1000 + int(j['usingtime'][9:12])
                fasttime = int(fast['usingtime'][0:2])*3600000 + int(fast['usingtime'][3:5])*60000 + int(fast['usingtime'][6:8])*1000 + int(fast['usingtime'][9:12])
                if jtime<fasttime:
                    fast = j
                elif jtime == fasttime:
                    if int(j['wrongtime'])<int(fast['wrongtime']):
                        fast = j
                    elif int(j['wrongtime'])==int(fast['wrongtime']):
                        pass #先不做
            #add to json
            jsonlist.append(fast)
            #remove from records
            records.remove(fast)
    sortjson = json.dumps(jsonlist)
    print("find data")
    return Response(sortjson, mimetype='text/json')