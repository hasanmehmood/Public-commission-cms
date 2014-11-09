from flask import render_template, flash, redirect, jsonify, request
from flask.ext.login import login_user, logout_user, current_user, login_required, UserMixin
from app import app, login_manager
from forms import LoginForm, AddContactForm, AddUserForm, AddDoc, AddComment
import pymongo
from pymongo import MongoClient
import datetime
import sys
from models import User
from bson.objectid import ObjectId
import json

MONGODB_URI = 'mongodb://ironman:stark@ds035280.mongolab.com:35280/test_db' 
SECRET_KEY_ADMIN = '123456789'

"""
    An index page for displaying all the Artices posted by Admins of the CMS
"""
@app.route('/')
@app.route('/index')
@login_required
def index():
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    docs = db.docs
    docs = docs.find()
    if current_user.sec == SECRET_KEY_ADMIN:
        admin = 1
    else:
        admin = 0
    return render_template("index.html",
        title = 'Home',
        admin = admin,
        user = current_user,
        docs = docs)

"""
    login page, the page has sign up and sign in options
"""
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        users = db.users
        for user in users.find():
            if user['username'] == form.username.data and user['password'] == form.password.data:
                u = User.get(str(user['_id']))
                login_user(u, remember=True)
                return redirect('index')
                flash("Logged in successfully.")
                return redirect("/index")

    return render_template('login.html', 
        title = 'Sign In',
        form = form)

"""
    Add new Document Page
"""
@app.route('/adddoc', methods = ['GET', 'POST'])
@login_required
def adddoc():
    form = AddDoc()
    if current_user.sec == SECRET_KEY_ADMIN:
        admin = 1
    else:
        admin = 0

    if form.validate_on_submit():
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        docs = db.docs
        newDoc = {
            "title": form.title.data,
            "content": form.content.data,
            "posted_by": current_user.username
        }
        docs.insert(newDoc)
        return redirect('/index')

    return render_template('adddoc.html', 
        user = current_user,
        admin = admin,
        title = 'Add New Document',
        form = form)

"""
    Edit previously posted article
"""
@app.route('/editdoc/<docid>', methods = ['GET', 'POST'])
@login_required
def editdoc(docid):
    form = AddDoc()
    if current_user.sec == SECRET_KEY_ADMIN:
        admin = 1
    else:
        admin = 0
    if form.validate_on_submit():
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        docs = db.docs
        newDoc = {
            "title": form.title.data,
            "content": form.content.data
        }
        docs.update({'_id': ObjectId(docid)}, newDoc, upsert=False)
        return redirect('/index')
    
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    docs = db.docs
    doc = docs.find({"_id": ObjectId(docid)})
    
    return render_template('editdoc.html', 
        user = current_user,
        title = 'Add New Document',
        doc = doc,
        admin = admin,
        form = form)

"""
    Sign up Page
"""
@app.route('/adduser', methods = ['GET', 'POST'])
def adduser():
    form = AddUserForm()

    if form.validate_on_submit():
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        users = db.users
        if form.sec.data == SECRET_KEY_ADMIN:
            newUser = {
                "username": form.username.data,
                "password": form.password.data,
                "contact": form.contact.data,
                "email": form.email.data,
                "sec": form.sec.data,
                "admin": "1"
            }
        else:
            newUser = {
                "username": form.username.data,
                "password": form.password.data,
                "contact": form.contact.data,
                "email": form.email.data,
                "sec": form.sec.data,
                "admin": "0"
            }
        users.insert(newUser)
        users = db.users
        
        for user in users.find():
            if user['username'] == form.username.data and user['password'] == form.password.data:
                u = User.get(str(user['_id']))
                login_user(u, remember=True)
                return redirect('index')
                flash("Logged in successfully.")
                return redirect("/index")

        return redirect('/login')
    return render_template('adduser.html',
        title = 'Add New User',
        form = form)

"""
    A Document and all comments related to that document will be displayed
"""
@app.route('/opendoc/<docid>', methods = ['GET', 'POST'])
@login_required
def opendoc(docid):
    form = AddComment();
    if current_user.sec == SECRET_KEY_ADMIN:
        admin = 1
    else:
        admin = 0
    if form.validate_on_submit():
        client = MongoClient(MONGODB_URI)
        db = client.get_default_database()
        comments = db.comments
        newComment = {
            "name": form.name.data,
            "comment": form.comment.data,
            "doc_id": docid
        }
        comments.insert(newComment)

    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    docs = db.docs
    doc = docs.find({"_id": ObjectId(docid)})
    comments = db.comments
    comments = comments.find({"doc_id": docid})
    return render_template("opendoc.html",
        title = 'Home',
        form = form,
        admin = admin,
        user = current_user,
        comments = comments,
        doc = doc)

"""
    Delete a Document
"""
@app.route('/deletedoc/<docid>')
@login_required
def deletedoc(docid):
    if current_user.sec == SECRET_KEY_ADMIN:
        admin = 1
    else:
        admin = 0
    client = MongoClient(MONGODB_URI)
    db = client.get_default_database()
    docs = db.docs
    docs.remove({"_id": ObjectId(docid)})
    docs = docs.find()
    return render_template("index.html",
        title = 'Home',
        admin = admin,
        user = current_user,
        docs = docs)

"""
    About us Page
"""
@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")


@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return 
    None based on the userid.
    The userid was stored in the session environment by Flask-Login.  
    user_loader stores the returned User object in current_user during every 
    flask request. 
    """

    return User.get(str(userid))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


def pretty_dump(input):
    return json.dumps(input, sort_keys=False, indent=4, separators=(',', ': '))