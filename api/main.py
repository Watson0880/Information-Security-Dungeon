from flask import Flask, request, flash, url_for, redirect, render_template, make_response, session, Response, jsonify
from flask_cors import CORS
from datetime import timedelta
import os
import json
import time
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get('securitykey')
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
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

@app.route('/User',methods=['GET','POST'])
def getuser():
    print(session.get('username'))
    if session.get('username') is None:
        print(session.get('username'))
        return redirect(url_for('getlogin'))
    if request.method == 'POST':
        if request.values.get('changepassword') == "變更密碼":
            uri = os.environ.get('URL')
            db_name = "rank"
            collection_name = "User"
            client = MongoClient(uri)
            database = client[db_name]
            collection = database[collection_name]
            users = collection.find_one({"username": session['username']})
            if users['password'] == request.form['oldpassword']:
                collection.update_one({"username":session['username']},{"$set": { "password": request.form['newpassword'] }})
                return redirect(url_for('getuser'))
            else:
                flash('密碼錯誤', 'error')
        if request.values.get('logout') == "Logout":
            session['username'] = None
            return redirect(url_for('getMainPage'))
    return render_template('/User.html')

@app.route('/forum')
def getforum():
    return render_template('/forum.html')

@app.route('/newarticle',methods=['GET','POST'])
def Newarticle():
    if session.get('username') is None:
        print(session.get('username'))
        return redirect(url_for('getlogin'))
    if request.method == 'POST':
        if request.form['name'] == "" or request.form['context'] == "":
            flash('請輸入標題或內容', 'error')
        else:
            uri = os.environ.get('URL')
            db_name = "rank"
            collection_name = "Article"
            client = MongoClient(uri)
            database = client[db_name]
            collection = database[collection_name]
            t = time.time()
            t1 = time.localtime(t)
            t2 = time.strftime('%Y/%m/%d %H:%M:%S',t1)
            collection.insert_one({'art-title':request.form['name'],'art-txt':[request.form['context']],'art-auth':[session.get('username')],'lastuploadtime':t2})
            return redirect(url_for('getforum'))
    return render_template('/newarticle.html')

@app.route('/findarticle/<_id>', methods = ["GET","DELETE"])
def findarticle(_id):
    if request.method == 'DELETE':
        uri = os.environ.get('URL')
        db_name = "rank"
        collection_name = "Article"
        client = MongoClient(uri)
        database = client[db_name]
        collection = database[collection_name]
        t = time.time()
        t1 = time.localtime(t)
        t2 = time.strftime('%Y/%m/%d %H:%M:%S',t1)
        datas = collection.find_one({"_id": ObjectId(_id)},{'art-txt':1})
        datas['art-txt'][request.values.get('deletebutton')] = "該回覆已被刪除"
        datas['lastuploadtime'] = t2
        collection.update_one({"_id": ObjectId(_id)},{"$set":{'art-txt':datas['art-txt']}})
        collection.update_one({"_id": ObjectId(_id)},{"$set":{'lastuploadtime':t2}})
        return render_template('/article.html',data={"_id":str(datas['_id']),'art-auth':datas['art-auth'],"art-title":datas['art-title'],"art-txt":datas['art-txt'],'lastuploadtime':datas['lastuploadtime'],'username':session.get('username')})
    uri = os.environ.get('URL')
    db_name = "rank"
    collection_name = "Article"
    client = MongoClient(uri)
    database = client[db_name]
    collection = database[collection_name]
    datas = collection.find_one({"_id": ObjectId(_id)})
    print(_id)
    print(datas)
    data = {"_id":str(datas['_id']),'art-auth':datas['art-auth'],"art-title":datas['art-title'],"art-txt":datas['art-txt'],'lastuploadtime':datas['lastuploadtime']}
    data = json.dumps(data) 
    return render_template('/article.html',data={"_id":str(datas['_id']),'art-auth':datas['art-auth'],"art-title":datas['art-title'],"art-txt":datas['art-txt'],'lastuploadtime':datas['lastuploadtime'],'username':session.get('username')})

@app.route('/reply/<_id>', methods = ["GET","POST"])
def reply(_id):
    if request.method == 'POST':
        uri = os.environ.get('URL')
        db_name = "rank"
        collection_name = "Article"
        client = MongoClient(uri)
        database = client[db_name]
        collection = database[collection_name]
        datas = collection.find_one({"_id": ObjectId(_id)})
        if request.form['context'] == "":
            flash('請輸入內容', 'error')
        else:
            t = time.time()
            t1 = time.localtime(t)
            t2 = time.strftime('%Y/%m/%d %H:%M:%S',t1)
            datas['art-auth'].append(session.get('username'))
            datas['art-txt'].append(request.form['context'])
            datas['lastuploadtime'] = t2
            collection.update_one({"_id": ObjectId(_id)},{"$set":{'art-auth':datas['art-auth']}})
            collection.update_one({"_id": ObjectId(_id)},{"$set":{'art-txt':datas['art-txt']}})
            collection.update_one({"_id": ObjectId(_id)},{"$set":{'lastuploadtime':t2}})
            return render_template('/article.html',data={"_id":str(datas['_id']),'art-auth':datas['art-auth'],"art-title":datas['art-title'],"art-txt":datas['art-txt'],'lastuploadtime':datas['lastuploadtime'],'username':session.get('username')})
    return render_template('/reply.html',data={"_id":_id})


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
    print(session.get('username'))
    if session.get('username')==None:
        j = {'islogin': 0,'username':"No"}
        j = json.dumps(j)
        return Response(j, mimetype='text/json')
    else:
        j = {'islogin': 1,'username':session.get('username')}
        j = json.dumps(j)
        return Response(j, mimetype='text/json')

@app.route('/gettitle',methods=["GET"])
def gettitle():
    uri = os.environ.get('URL')
    db_name = "rank"
    collection_name = "Article"
    client = MongoClient(uri)
    database = client[db_name]
    collection = database[collection_name]
    jsonlist = []
    datas = collection.find({},{"_id": 1,'art-auth':1, "art-title":1,'lastuploadtime':1})
    for data in datas:
        article = {"_id":str(data['_id']),'art-auth':data['art-auth'][0],"art-title":data['art-title'],'lastuploadtime':data['lastuploadtime']}
        jsonlist.append(article)
    j = json.dumps(jsonlist) 
    return Response(j, mimetype='text/json')