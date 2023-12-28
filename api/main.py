from flask import Flask, request, flash, url_for, redirect, render_template, make_response, session, Response, jsonify
from flask_cors import CORS
import os
import json
from pymongo.mongo_client import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app, supports_credentials=True)

@app.route('/')
@app.route('/MainPage')
def getMainPage():
    return render_template('/MainPage.html')

@app.route('/rank')
def getrank():
    return render_template('/rank.html')

@app.route('/introduce')
def getintroduce():
    return render_template('/Introduce.html')

@app.route('/login',methods=['GET',"POST"])
def getlogin():
    if request.method == 'POST':
        if  request.form['username'] == "" or request.form['password'] == "":
            flash('未填入帳號密碼', 'error')
        else:
            uri = os.environ.get('URL')
            db_name = "rank"
            collection_name = "User"
            client = MongoClient(uri)
            database = client[db_name]
            collection = database[collection_name]
            users = collection.find_one({"username": request.form['username']})
            print(users)
            if users is not None:
                if users['password'] == request.form['password']:
                    session['username'] = request.form['username']
                    return redirect(url_for('getMainPage'))
                else:
                    flash('密碼錯誤', 'error')
            else:
                flash('不存在的用戶', 'error')
    return render_template('/Login.html')

@app.route('/register',methods=['GET',"POST"])
def getregister():
    if request.method == 'POST':
        if request.form['username'] == "" or request.form['password'] == "" or request.form['confirmpassword'] == "":
            flash('未填入完整', 'error')
        else:
            uri = os.environ.get('URL')
            db_name = "rank"
            collection_name = "User"
            client = MongoClient(uri)
            database = client[db_name]
            collection = database[collection_name]
            users = collection.find_one({"username": request.form['username']})
            try:
                for i in users:
                    print(i)
            except:
                print(users)
            if users is None:
                if request.form['confirmpassword'] == request.form['password']:
                    collection.insert_one({'username':request.form['username'],'password':request.form['password']}) #加入資料庫
                    return redirect(url_for('getMainPage'))
                else:
                    flash('確認密碼與密碼不同', 'error')
            else:
                flash('已存在的用戶', 'error')
    return render_template('/Register.html')

@app.route('/User',methods=['GET'])
def getuser():
    if session.get('username') is None:
        redirect(url_for('getlogin'))
    return render_template('/User.html')

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
        records.append({'uid':i['uid'], 'usingtime':i['usingtime'], 'wrongtime':i['wrongtime'],'uploadtime':i['uploadtime']})
    jsonlist = []
    if len(records)>100:
        for i in range(100):
            fast = {'uid':0,'usingtime':'24:00:00:0000000','wrongtime':0,'uploadtime':0}
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
            fast = {'uid':0,'usingtime':'24:00:00:0000000','wrongtime':0,'uploadtime':0}
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

@app.route('/checklogin',methods=["GET"])
def checklogin():
    if session.get('username') is None:
        j = {'islogin': 0,'username':"No"}
        j = json.dumps(j)
        return Response(j, mimetype='text/json')
    else:
        j = {'islogin': 1,'username':session.get('username')}
        j = json.dumps(j)
        return Response(j, mimetype='text/json')