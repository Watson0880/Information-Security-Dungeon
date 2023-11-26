from flask import Flask, render_template
from flask import request
from flask import Response
from flask_cors import CORS
import os
import json
from pymongo.mongo_client import MongoClient



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
