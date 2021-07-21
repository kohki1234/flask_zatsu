from flask import Flask, render_template, g, request, redirect, url_for
import flask 
from markupsafe import escape
import os
import sqlite3
import urllib.request
from flask_sqlalchemy import SQLAlchemy
import flask_oauthlib.client
import urllib.parse
from jose import jwt

app = Flask(__name__)
app.secret_key = '9q9QpZQl8ooW'


# auth0 setting
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')


oauth = flask_oauthlib.client.OAuth(app)
auth0 = oauth.remote_app(
    'auth0',
    consumer_key=AUTH0_CLIENT_ID,
    consumer_secret=AUTH0_CLIENT_SECRET,
    request_token_params={
        'scope': 'openid profile',
        'audience': 'https://{}/userinfo'.format(AUTH0_DOMAIN),
    },
    base_url='https://{}'.format(AUTH0_DOMAIN),
    access_token_method='POST',
    access_token_url='/oauth/token',
    authorize_url='/authorize',
)

# database connection settings
database_url = str(os.environ.get('DATABASE_URL'))
db_uri = database_url.replace("://", "ql://", 1) 

# db_uri =  "postgresql://localhost/flasknote" # when testing locally
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app) 

class Entry(db.Model): 
    __tablename__ = "entries" 
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(), nullable=False) 
    body = db.Column(db.String(), nullable=False) 

@app.route('/')
def return_main():
    return render_template('main.html')

@app.route('/main')
def hello_world():
    if 'profile' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    
    else:
        entries = Entry.query.all()
        return render_template('index.html', entries=entries)

@app.route('/login')
def login():
    return auth0.authorize(callback=flask.url_for('auth_callback', _external=True))

@app.route('/callback')
def auth_callback():
    # Auth0がくれた情報を取得する。
    resp = auth0.authorized_response()
    if resp is None:
        return 'nothing data', 403


    # 署名をチェックするための情報を取得してくる。
    with urllib.request.urlopen('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)) as jwks:
        key = jwks.read()


    # JWT形式のデータを復号して、ユーザーについての情報を得る。
    # ついでに、署名が正しいかどうか検証している。
    try:
        payload = jwt.decode(resp['id_token'], key, audience=AUTH0_CLIENT_ID)
    except Exception as e:
        print(e)
        return 'something wrong', 403  # 署名がおかしい。


    # flaskのSessionを使ってcookieにユーザーデータを保存。
    flask.session['profile'] = {
        'id': payload['sub'],
        'name': payload['name'],
        'picture': payload['picture'],
    }
    print(payload)


    # マイページに飛ばす。
    return flask.redirect(flask.url_for('mypage'))


@app.route('/logout')
def logout():
    del flask.session['profile']  # cookieから消す


    # Auth0にも伝える
    params = {'returnTo': flask.url_for('hello_world', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return flask.redirect(auth0.base_url + '/v2/logout?' + urllib.parse.urlencode(params))


@app.route('/mypage')
def mypage():
    if 'profile' not in flask.session:
        return flask.redirect(flask.url_for('login'))


    return '''
        <img src="{picture}"><br>
        name: <b>{name}</b><br>
        ID: <b>{id}</b><br>
        <br>
        <a href="/">back to top</a>
        <a href="/logout">logout</a>
    '''.format(**flask.session['profile'])

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

if __name__ == '__main__':
    app.run(debug=True)
