from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from config import SECRET_KEY
import MySQLdb
import nvdlib
import requests


app = Flask(__name__)
app.secret_key = "123321"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123456"
app.config["MYSQL_DB"] = "snooper"

db = MySQL(app)

fernet = Fernet(SECRET_KEY)


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form ['email']
            password = request.form ['password']
            cursor= db.connection.cursor (MySQLdb.cursors.DictCursor)
            cursor.execute ("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone ()
            if user is not None:
                encrypted_password = user['password']
                decrypted_password = fernet.decrypt(encrypted_password).decode()
                if decrypted_password == password:
                    session['loginsuccess'] = True
                    return redirect (url_for('dash'))
            else:
                return redirect (url_for('index'))

    return render_template("login.html")


@app.route('/register', methods=['GET','POST'])
def new_user():
    if "one" in request.form and "two" in request.form and "three" in request.form:
        name = request.form ['one']
        email = request.form ['two']
        password = request.form ['three']
        encrypted_password = fernet.encrypt(password.encode())
        cur = db.connection.cursor (MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO snooper.users (email, password, name) VALUES (%s, %s, %s)", (email, encrypted_password, name))
        db.connection.commit()
        return redirect (url_for('index'))
    return render_template("register.html")


@app.route('/dashboard')
def dash():
    if session['loginsuccess'] == True:
        return render_template('dashboard.html')
    
@app.route('/about')
def about():
    if session['loginsuccess'] == True:
        return render_template('about.html')

@app.route('/profile')
def profile():
    if session['loginsuccess'] == True:
        return render_template('profile.html')
    
    
@app.route('/logout')
def logout ():
    session.pop ('loginsuccess', None)
    return redirect (url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_cve():
    if request.method == 'POST':
        searchword = request.form['searchkeyword']
        params = {'description.keyword': searchword}
        response = requests.get('https://cve.mitre.org/cgi-bin/cvekey.cgi', params=params)
        results = []
        for line in response.text.splitlines():
            if line.startswith('<tr><td><a href="/cgi-bin/cvename.cgi?name='):
                cve_id = line.split('name=')[1].split('"')[0]
                results.append(cve_id)
        return render_template('dashboard.html', searchword=searchword, results=results)
    else:
        return render_template('login.html')

""""
@app.route('/search', methods=['GET', 'POST'])
def search_cve():
    if request.method == 'POST':
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=30)
        searchword = request.form['searchkeyword']
        results = nvdlib.searchCVE(keywordSearch=searchword, pubStartDate=start, pubEndDate=end, key='49a35609-1545-41c4-83d4-9e5ffc4eb033')
        return render_template('dashboard.html', results=results)
    else:
        return render_template('dashboard.html')
"""

if __name__ == '__main__':
    app.run(debug=True)
    