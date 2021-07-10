from flask import Flask, render_template, g, request, redirect, url_for 
from markupsafe import escape
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db_uri = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or "postgresql://localhost/flasknote"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app) 

class Entry(db.Model): 
    __tablename__ = "entries" 
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(), nullable=False) 
    body = db.Column(db.String(), nullable=False) 

@app.route('/')
def hello_world():
    entries = Entry.query.all()
    return render_template('index.html', entries=entries)


@app.route('/add')
def add_comment():
    entries = Entry.query.all()
    return render_template('add.html', entries=entries)

@app.route('/post', methods=['POST'])
def add_entry():
    # create a new entry instance
    entry = Entry()

    # assign form information to columns
    entry.title = request.form['title']
    entry.body = request.form['body']

    # add information
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('hello_world'))