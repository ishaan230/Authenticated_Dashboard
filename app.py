from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import config
import certifi
import requests
from requests import get

app = Flask(__name__)
app.config.from_object(config)

#set up MongoDB
client = MongoClient(config.MONGO_URI,tlsCAFile=certifi.where())
db = client.gettingStarted
col = db.usrpass

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = col.find_one({'username': username})
        if user and password==user['password']:
            session['username'] = username
            return redirect(url_for('welcome'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            if col.find_one({'username': username}):
                return render_template('register.html', error='UserName Already Exists!')

            col.insert_one({'username': username, 'password': password})
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Passwords do not match')
    return render_template('register.html')

@app.route('/welcome')
def welcome():
    print(session)
    print(type(session))
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/call_external_api')
def joke_generator():
    headers = {
        'Content-Type': 'application/json'
    }
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url,headers=headers)
    response = (response.json())
    print(type(response))
    setup = response['setup']
    punchline = (response['punchline'])
    if 'username' in session:
        return render_template('welcome.html', username=session['username'],setup=setup, punchline=punchline)
    return "Error"

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)