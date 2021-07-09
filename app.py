from flask import Flask, render_template 
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', username="John")

@app.route('/routing')
def route():
    return 'hello routing page is working'


@app.route('/user/<userid>')
def show_user_profile(userid):
    return 'the user id is {}'.format(userid)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'post id is {}'.format(post_id)