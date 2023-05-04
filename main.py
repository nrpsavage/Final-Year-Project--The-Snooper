from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from config import SECRET_KEY
import MySQLdb
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = "123321"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123456"
app.config["MYSQL_DB"] = "snooper"

db = MySQL(app)

fernet = Fernet(SECRET_KEY)


## Code for the log in and sign up with encryption and decription on password.
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



## Routes to access the different pages of my application.
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



## Code for the search function, makes use of an API to search for CVEs.
@app.route('/dashboard/search', methods=['GET', 'POST'])
def search_cve():
    if request.method == 'POST':
        searchword = request.form['searchkeyword']
        url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={searchword}+2023"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            return render_template('dashboard.html', results=[])
        try:
            results = []
            soup = BeautifulSoup(response.text, 'html.parser')
            cve_table = soup.find_all('table')[2]
            for row in cve_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                cve_id = cols[0].find('a').text
                description = cols[1].text.strip()
                results.append({'id': cve_id, 'summary': description})
            return render_template('dashboard.html', results=results)
        except ValueError as e:
            print(f"Failed to decode response as JSON: {response.content}")
            return render_template('dashboard.html', results=[])
    else:
        return render_template('dashboard.html')


## Code below is what I have utilised to gather the different scoring metrics
@app.route('/score', methods=['POST'])
def score():
    cve_id = request.form['id']
    summary = request.form['summary']
    cve_url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
    nist_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
    google_url = f"https://www.google.ie/search?q={cve_id}"
    
    # Scrape the CVSS score from the NIST website
    response = requests.get(nist_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        score = "N/A"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        cvss_elem = soup.find('span', {'data-testid': 'vuln-cvss3-panel-score'})
        if cvss_elem is not None:
            score = cvss_elem.text.strip()
        else:
            score = "N/A"
    
    response = requests.get(google_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        score = "N/A"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        search_result = soup.find('div', {'id':'result-stats'})
        if search_result is not None:
            google = search_result.text.strip()
        else:
            google = "N/A"
    
    return render_template('scoring.html', id=cve_id, summary=summary, cvss_score=score, url=cve_url, google_result=google)


if __name__ == '__main__':
    app.run(debug=True)
    