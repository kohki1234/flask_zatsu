from flask import Flask, render_template ,url_for, request, g
from markupsafe import escape
import os
import sqlite3

app = Flask(__name__)

@app.route('/')
def hello_world():
    entries = get_db().execute('select title, body from entries').fetchall()
    return render_template('index.html', entries=entries)


# connect database 
def connect_db():
    db_path = os.path.join(app.root_path,'flasknote.db')
    rv = sqlite3.connect(db_path)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/routing')
def route():
    return 'hello routing page is working'


@app.route('/user/<userid>')
def show_user_profile(userid):
    return 'the user id is {}'.format(userid)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'post id is {}'.format(post_id)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        return 'post method is called'
    else:
        return 'get method is called'

# debugging method to printout the url for each endpoint
with app.test_request_context():
    print('test_request_context method is called!')
    print(url_for('hello_world'))
    print(url_for('route'))

    print(url_for('show_user_profile', userid='150'))
    # print(url_for('profile', username='John Doe'))