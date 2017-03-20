"""
Routes and views for the flask application.
"""

from datetime import datetime
import MySQLdb
from flask import render_template,request,redirect,session
from FlaskWebProject import app
import base64
import os

def connection():
    db = MySQLdb.connect(host="us-cdbr-azure-west-c.cloudapp.net",    # your host, usually localhost
                     user="***",         # your username
                     passwd="***",  # your password
                     db="testddb")
    return db

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


@app.route('/loginsuccess',methods=['POST'])
def login():
    """Renders the home page."""

    db=connection()
    cursor=db.cursor()
    userNam=request.form['userName']
    enteredPassword= request.form['password']
    checkloginquery="select password from userlogin where username='%s'" %(userNam)
    print checkloginquery
    cursor.execute(checkloginquery)
    for row in cursor.fetchall():
        storedpassword = row[0]
        if (enteredPassword == storedpassword):
            session['username']=userNam
            return render_template("contact.html")
        else:
            return render_template("index.html")
    db.commit()
    cursor.close()
    db.close()

    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )



@app.route('/inserttextNote', methods=['POST'])
def insertTextNote():
    db = connection()
    cursor = db.cursor()
    subject=request.form['subject']
    textnote = request.form['textnote']
    priority = request.form['priority']
    username=session['username']
    insertNoteQuery="insert into usernotes(username,Type,NoteText,subject,priority,time) values(%s,%s,%s,%s,%s,%s)"
    args=(username,'Note',textnote,subject,priority,datetime.now())
    cursor.execute(insertNoteQuery,args)
    db.commit()
    cursor.close()
    db.close()

    return "Text Note Added"

@app.route('/insertimageNote', methods=['POST'])
def insertimageNote():
    db = connection()
    cursor = db.cursor()
    subject=request.form['subjectimage']
    imagenote = request.files['noteimage']
    priority = request.form['priorityimage']
    username=session['username']
    imagefilename=imagenote.filename
    #obj=open(imagefilename,'rb').read()

    with open(imagefilename, "rb") as image_file:
        encoded_string = "data:image/jpeg;base64,"+base64.b64encode(image_file.read())

    insertImageNoteQuery="insert into usernotes(username,Type,imageName,imageblob,subject,priority,time) values(%s,%s,%s,%s,%s,%s,%s)"
    args=(username,'Image',imagefilename,encoded_string,subject,priority,datetime.now())
    cursor.execute(insertImageNoteQuery,args)
    db.commit()
    cursor.close()
    db.close()

    return "Image Note Added"

@app.route('/showNotes',methods=['POST','GET'])
def showNotes():
    if request.method=='GET':
        db = connection()
        cursor = db.cursor()
        sortcriteria=request.args.get('sort')
        if sortcriteria is None:
            sortcriteria="time"
        username=session['username']
        getTextNotesquery = "select * from usernotes where username='%s'" % (username) +" order by "+sortcriteria
        print getTextNotesquery
        cursor.execute(getTextNotesquery)
        textNotesList=[]
        for row in cursor.fetchall():
            #print row
            notesdict={}
            notesdict['Note_id'] = row[0]
            notesdict['Type'] = row[2]
            notesdict['NoteText'] = row[3]
            notesdict['imageName'] = row[4]
            if row[4] is not None:
                #imagecontent=str(row[5])
                notesdict['imageblob'] = str(row[5])
            notesdict['subject'] = row[6]
            notesdict['priority'] = row[7]
            notesdict['time'] = row[8]
            textNotesList.append(notesdict)

        #print textNotesList
        #return "yguygy"
        return render_template("shownotes.html",textNotesList=textNotesList)
    if request.method=='POST':
        return "return post"


