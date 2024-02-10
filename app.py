from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import config
import certifi
import requests
from requests import get
from datetime import datetime

app = Flask(__name__)
app.config.from_object(config)

#set up MongoDB
client = MongoClient(config.MONGO_URI)
db = client.gettingStarted
col = db.usrpass
perdet = db.people
current_date = datetime.now().date()

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
        return render_template('welcome.html', username=session['username'],current_date=current_date)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
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
        return render_template('welcome.html', username=session['username'],setup=setup, punchline=punchline,current_date=current_date)
    return "Error"

@app.route('/gen_team')
def sub_team():
    if 'username' in session:
        return render_template('details.html')

@app.route('/form_submit', methods=['GET','POST'])
def form_submission():
    if request.method == 'POST':
        name1 = request.form['name1']
        name2 = request.form['name2']
        name3 = request.form['name3']
        name4 = request.form['name4']
        perdet.insert_one({'member1': name1,'member2': name2,'member3': name3,'member4': name4})
        return ("""
            <h1>Info Submitted!! xD</h1>
            <script>alert('Info Submited!')</script>
        """)
    else:
        print("Not in if")
    return render_template('details.html')



if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)