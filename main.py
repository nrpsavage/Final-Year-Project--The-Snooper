from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
from config import SECRET_KEY
from config import app_key
import MySQLdb
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

app = Flask(__name__)

#Connection for database
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql123456"
app.config["MYSQL_DB"] = "snooper"

db = MySQL(app)
app.secret_key = (app_key)
fernet = Fernet(SECRET_KEY)

# Routes to access the different pages of my application.
@app.route('/dashboard')
def dash():
    encrypted_id = session.get('user_id')
    if encrypted_id is None:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/about')
def about():
    encrypted_id = session.get('user_id')
    if encrypted_id is None:
        return redirect(url_for('index'))
    return render_template('about.html')

@app.route('/logout')
def logout ():
    session.pop ('user_id', None)
    return redirect (url_for('index'))



# Code for the log in and sign up with encryption and decription on password.
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
                    user_id = user['my_id']
                    encrypted_id = fernet.encrypt(str(user_id).encode()).decode()
                    session['user_id'] = encrypted_id
                    return redirect (url_for('dash'))
            else:
                return redirect (url_for('index'))

    return render_template("login.html")



@app.route('/register', methods=['GET','POST'])
def new_user():
    if "name" in request.form and "email" in request.form and "pass" in request.form:
        name = request.form ['name']
        email = request.form ['email']
        password = request.form ['pass']
        encrypted_password = fernet.encrypt(password.encode())
        cursor = db.connection.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO snooper.users (email, password, name, date_created) VALUES (%s, %s, %s,NOW())", (email, encrypted_password, name))
        db.connection.commit()
        return redirect (url_for('index'))
    return render_template("register.html")



# Code below is used to get the users information in the database and display it on the page.
@app.route('/profile', methods=['GET','POST'])
def profile():
    encrypted_id = session.get('user_id')
    if encrypted_id is None:
        return redirect(url_for('index'))

    id = int(fernet.decrypt(encrypted_id.encode()).decode())
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM users WHERE my_id={id}")
    user1 = cursor.fetchone()
    cursor.execute(f"SELECT * FROM apps WHERE user_id={id}")
    user2 = cursor.fetchall()

    name = user1['name']
    email = user1['email']
    date = user1['date_created']
    company = user1['company_name']

    if request.method == 'POST':
        app_name = request.form['app_name']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO apps (user_id, app_name) VALUES (%s, %s)", (id, app_name))
        db.connection.commit()
        ##

    return render_template('profile.html', name=name, email=email, date=date, company=company, user2=user2)

# Code below is used to change the users variables in the database.
@app.route('/edit', methods=['GET','POST'])
def change():
    if "name" in request.form and "email" in request.form and "company" in request.form:
        name = request.form ['name']
        email = request.form ['email']
        company = request.form ['company']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"UPDATE users SET email=%s, name=%s, company_name=%s", (email, name, company))
        db.connection.commit()
        return render_template('dashboard.html')
    return render_template('edit.html')



# Code for the search function, makes use of an API to search for CVEs.
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
    


@app.route('/dashboard/quicksearch', methods=['GET', 'POST'])
def quick_search():
    encrypted_id = session.get('user_id')
    if request.method == 'POST':
        user_id = int(fernet.decrypt(encrypted_id.encode()).decode())
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM apps WHERE user_id={user_id}")        
        quicksearch = cursor.fetchone()
        url = f"https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword={quicksearch}+2023"
        response = requests.get(url)
        if quicksearch == ():
            return render_template('dashboard.html')
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



# Code below is what I have utilised to gather the different scoring metrics
@app.route('/score', methods=['POST'])
def score():
    cve_id = request.form['id']
    summary = request.form['summary']
    cve_url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
    nist_url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"


    # Check if any of the keywords appear in the summary
    #Below is a list of many keywords found in CVE's, the list hardcoded below is early version mainly for testing.
    keywords = ["buffer overflow", "cross-site scripting", "sql injection", "authentication bypass", "remote code execution", "denial of service", "information disclosure", "privilege escalation", "arbitrary file upload", "command injection", "directory traversal", "clickjacking", "cross-site request forgery", "xml external entity", "integer overflow", "insecure deserialization", "unvalidated input", "improper input validation", "insufficient access control", "broken access control", "xml injection", "local file inclusion", "path traversal", "buffer underflow", "buffer overread", "memory leak", "format string vulnerability", "heap overflow", "stack overflow", "use-after-free vulnerability", "integer underflow", "insufficient entropy"]

    keyword_matches = [keyword for keyword in keywords if keyword in summary.lower()]
    key_match = ", ".join([kw.title() for kw in keyword_matches])



    # Scrape the CVSS3 score from the NIST website
    response = requests.get(nist_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        score3 = "Error"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        cvss3_elem = soup.find('span', {'class': 'severityDetail'})
        if cvss3_elem is not None:
            score3 = cvss3_elem.text.strip()
        else:
            score3 = "N/A"



    # Scrape the CVSS2 score from the NIST website
    response = requests.get(nist_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        score2 = "Error"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        cvss2_elem = soup.find(id="Cvss2CalculatorAnchorNA")
        if cvss2_elem is not None:
            score2 = cvss2_elem.text.strip()
        else:
            score2 = "N/A"



    #Scrape the NIST site to see if CVE's are being exploited
    response = requests.get(nist_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        exploit = "Error"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        exploit_result = soup.find(id="vulnCisaExploit")
        if exploit_result is not None:
            exploit = "Being Exploited"
        else:
            exploit = "Not Exploited"   



    #Scrape Google for the total search results of CVE's
    params = {
        "engine": "google",
        "q": cve_id,
        "api_key": 'aa4e0796efda079482a2f396a4c38455611928b4b843bf2c43a94685f564fcd5'
    }
    try:
        search = GoogleSearch(params)
        result = search.get_dict() 
        if "organic_results" in result and len(result["organic_results"]) > 0:
            search_stats_str = result["search_information"]["total_results"]
            search_stats_int = int( search_stats_str)
            google = f"{search_stats_int}"
        else:
            google = "N/A"
    except Exception as e:
        print(f"Error retrieving Google search results for {cve_id}: {str(e)}")
        google = "Error"



    # Code below is the function for my personal scoring system: Snooper Scoring.
    if search_stats_int == "N/A":
        goog=0
    else:
        if search_stats_int >= 1 and search_stats_int <= 999:
            goog=1
        elif search_stats_int >=1000 and search_stats_int <=9999:
            goog=2
        elif search_stats_int >=10000 and search_stats_int <=99999:
            goog=3
        elif search_stats_int >=100000:
            goog=4

    if score3 == "N/A":
        cvss3=0
    else:
        if score3 == "10.0 CRITICAL":
            cvss3=8
        elif score3 == "9.9 CRITICAL":
            cvss3=8
        elif score3 == "9.8 CRITICAL":
            cvss3=8
        elif score3 == "9.7 CRITICAL":
            cvss3=8
        elif score3 == "9.6 CRITICAL":
            cvss3=8
        elif score3 == "9.5 CRITICAL":
            cvss3=8
        elif score3 == "9.4 CRITICAL":
            cvss3=8
        elif score3 == "9.3 CRITICAL":
            cvss3=8
        elif score3 == "9.2 CRITICAL":
            cvss3=8
        elif score3 == "9.1 CRITICAL":
            cvss3=8
        elif score3 == "9.0 CRITICAL":
            cvss3=8
        elif score3 == "8.9 HIGH":
            cvss3=6
        elif score3 == "8.8 HIGH":
            cvss3=6
        elif score3 == "8.7 HIGH":
            cvss3=6
        elif score3 == "8.6 HIGH":
            cvss3=6
        elif score3 == "8.5 HIGH":
            cvss3=3
        elif score3 == "8.4 HIGH":
            cvss3=6
        elif score3 == "8.3 HIGH":
            cvss3=6
        elif score3 == "8.2 HIGH":
            cvss3=6
        elif score3 == "8.1 HIGH":
            cvss3=6
        elif score3 == "8.0 HIGH":
            cvss3=6
        elif score3 == "7.9 HIGH":
            cvss3=6
        elif score3 == "7.8 HIGH":
            cvss3=6
        elif score3 == "7.7 HIGH":
            cvss3=6
        elif score3 == "7.6 HIGH":
            cvss3=6
        elif score3 == "7.5 HIGH":
            cvss3=6
        elif score3 == "7.4 HIGH":
            cvss3=6
        elif score3 == "7.3 HIGH":
            cvss3=6
        elif score3 == "7.2 HIGH":
            cvss3=6
        elif score3 == "7.1 HIGH":
            cvss3=6
        elif score3 == "7.0 HIGH":
            cvss3=6
        elif score3 == "6.9 MEDIUM":
            cvss3=4
        elif score3 == "6.8 MEDIUM":
            cvss3=4
        elif score3 == "6.7 MEDIUM":
            cvss3=4
        elif score3 == "6.6 MEDIUM":
            cvss3=4
        elif score3 == "6.5 MEDIUM":
            cvss3=4
        elif score3 == "6.4 MEDIUM":
            cvss3=4
        elif score3 == "6.3 MEDIUM":
            cvss3=4
        elif score3 == "6.2 MEDIUM":
            cvss3=4
        elif score3 == "6.1 MEDIUM":
            cvss3=4
        elif score3 == "6.0 MEDIUM":
            cvss3=4
        elif score3 == "5.9 MEDIUM":
            cvss3=4
        elif score3 == "5.8 MEDIUM":
            cvss3=4
        elif score3 == "5.7 MEDIUM":
            cvss3=4
        elif score3 == "5.6 MEDIUM":
            cvss3=4
        elif score3 == "5.5 MEDIUM":
            cvss3=4
        elif score3 == "5.4 MEDIUM":
            cvss3=4
        elif score3 == "5.3 MEDIUM":
            cvss3=4
        elif score3 == "5.2 MEDIUM":
            cvss3=4
        elif score3 == "5.1 MEDIUM":
            cvss3=4
        elif score3 == "5.0 MEDIUM":
            cvss3=4
        elif score3 == "4.9 MEDIUM":
            cvss3=4
        elif score3 == "4.8 MEDIUM":
            cvss3=4
        elif score3 == "4.7 MEDIUM":
            cvss3=4
        elif score3 == "4.6 MEDIUM":
            cvss3=4
        elif score3 == "4.5 MEDIUM":
            cvss3=4
        elif score3 == "4.4 MEDIUM":
            cvss3=4
        elif score3 == "4.3 MEDIUM":
            cvss3=4
        elif score3 == "4.2 MEDIUM":
            cvss3=4
        elif score3 == "4.1 MEDIUM":
            cvss3=4
        elif score3 == "4.0 MEDIUM":
            cvss3=4
        elif score3== "3.9 LOW":
            cvss3=2
        elif score3== "3.8 LOW":
            cvss3=2
        elif score3== "3.7 LOW":
            cvss3=2
        elif score3== "3.6 LOW":
            cvss3=2
        elif score3== "3.5 LOW":
            cvss3=2
        elif score3== "3.4 LOW":
            cvss3=2
        elif score3== "3.3 LOW":
            cvss3=2
        elif score3== "3.2 LOW":
            cvss3=2
        elif score3== "3.1 LOW":
            cvss3=2
        elif score3== "3.0 LOW":
            cvss3=2
        elif score3== "2.9 LOW":
            cvss3=2
        elif score3== "2.8 LOW":
            cvss3=2
        elif score3== "2.7 LOW":
            cvss3=2
        elif score3== "2.6 LOW":
            cvss3=2
        elif score3== "2.5 LOW":
            cvss3=2
        elif score3== "2.4 LOW":
            cvss3=2
        elif score3== "2.3 LOW":
            cvss3=2
        elif score3== "2.2 LOW":
            cvss3=2
        elif score3== "2.1 LOW":
            cvss3=2
        elif score3== "2.0 LOW":
            cvss3=2
        elif score3== "1.9 LOW":
            cvss3=2
        elif score3== "1.8 LOW":
            cvss3=2
        elif score3== "1.7 LOW":
            cvss3=2
        elif score3== "1.6 LOW":
            cvss3=2
        elif score3== "1.5 LOW":
            cvss3=2
        elif score3== "1.4 LOW":
            cvss3=2
        elif score3== "1.3 LOW":
            cvss3=2
        elif score3== "1.2 LOW":
            cvss3=2
        elif score3== "1.1 LOW":
            cvss3=2
        elif score3== "1.0 LOW":
            cvss3=2
        elif score3== "0.9 LOW":
            cvss3=2
        elif score3== "0.8 LOW":
            cvss3=2
        elif score3== "0.7 LOW":
            cvss3=2
        elif score3== "0.6 LOW":
            cvss3=2
        elif score3== "0.5 LOW":
            cvss3=2
        elif score3== "0.4 LOW":
            cvss3=2
        elif score3== "0.3 LOW":
            cvss3=2
        elif score3== "0.2 LOW":
            cvss3=2
        elif score3== "0.1 LOW":
            cvss3=2

    if score2 == "N/A":
        cvss2=0
    else:
        if score2 == "10.0 HIGH":
            cvss2=3
        elif score2 == "9.9 HIGH":
            cvss2=3
        elif score2 == "9.8 HIGH":
            cvss2=3
        elif score2 == "9.7 HIGH":
            cvss2=3
        elif score2 == "9.6 HIGH":
            cvss2=3
        elif score2 == "9.5 HIGH":
            cvss2=3
        elif score2 == "9.4 HIGH":
            cvss2=3
        elif score2 == "9.3 HIGH":
            cvss2=3
        elif score2 == "9.2 HIGH":
            cvss2=3
        elif score2 == "9.1 HIGH":
            cvss2=3
        elif score2 == "9.0 HIGH":
            cvss2=3
        elif score2 == "8.9 HIGH":
            cvss2=3
        elif score2 == "8.8 HIGH":
            cvss2=3
        elif score2 == "8.7 HIGH":
            cvss2=3
        elif score2 == "8.6 HIGH":
            cvss2=3
        elif score2 == "8.5 HIGH":
            cvss2=3
        elif score2 == "8.4 HIGH":
            cvss2=3
        elif score2 == "8.3 HIGH":
            cvss2=3
        elif score2 == "8.2 HIGH":
            cvss2=3
        elif score2 == "8.1 HIGH":
            cvss2=3
        elif score2 == "8.0 HIGH":
            cvss2=3
        elif score2 == "7.9 HIGH":
            cvss2=3
        elif score2 == "7.8 HIGH":
            cvss2=3
        elif score2 == "7.7 HIGH":
            cvss2=3
        elif score2 == "7.6 HIGH":
            cvss2=3
        elif score2 == "7.5 HIGH":
            cvss2=3
        elif score2 == "7.4 HIGH":
            cvss2=3
        elif score2 == "7.3 HIGH":
            cvss2=3
        elif score2 == "7.2 HIGH":
            cvss2=3
        elif score2 == "7.1 HIGH":
            cvss2=3
        elif score2 == "7.0 HIGH":
            cvss2=3
        elif score2 == "6.9 MEDIUM":
            cvss2=2
        elif score2 == "6.8 MEDIUM":
            cvss2=2
        elif score2 == "6.7 MEDIUM":
            cvss2=2
        elif score2 == "6.6 MEDIUM":
            cvss2=2
        elif score2 == "6.5 MEDIUM":
            cvss2=2
        elif score2 == "6.4 MEDIUM":
            cvss2=2
        elif score2 == "6.3 MEDIUM":
            cvss2=2
        elif score2 == "6.2 MEDIUM":
            cvss2=2
        elif score2 == "6.1 MEDIUM":
            cvss2=2
        elif score2 == "6.0 MEDIUM":
            cvss2=2
        elif score2 == "5.9 MEDIUM":
            cvss2=2
        elif score2 == "5.8 MEDIUM":
            cvss2=2
        elif score2 == "5.7 MEDIUM":
            cvss2=2
        elif score2 == "5.6 MEDIUM":
            cvss2=2
        elif score2 == "5.5 MEDIUM":
            cvss2=2
        elif score2 == "5.4 MEDIUM":
            cvss2=2
        elif score2 == "5.3 MEDIUM":
            cvss2=2
        elif score2 == "5.2 MEDIUM":
            cvss2=2
        elif score2 == "5.1 MEDIUM":
            cvss2=2
        elif score2 == "5.0 MEDIUM":
            cvss2=2
        elif score2 == "4.9 MEDIUM":
            cvss2=2
        elif score2 == "4.8 MEDIUM":
            cvss2=2
        elif score2 == "4.7 MEDIUM":
            cvss2=2
        elif score2 == "4.6 MEDIUM":
            cvss2=2
        elif score2 == "4.5 MEDIUM":
            cvss2=2
        elif score2 == "4.4 MEDIUM":
            cvss2=2
        elif score2 == "4.3 MEDIUM":
            cvss2=2
        elif score2 == "4.2 MEDIUM":
            cvss2=2
        elif score2 == "4.1 MEDIUM":
            cvss2=2
        elif score2 == "4.0 MEDIUM":
            cvss2=2
        elif score2== "3.9 LOW":
            cvss2=1
        elif score2== "3.8 LOW":
            cvss2=1
        elif score2== "3.7 LOW":
            cvss2=1
        elif score2== "3.6 LOW":
            cvss2=1
        elif score2== "3.5 LOW":
            cvss2=1
        elif score2== "3.4 LOW":
            cvss2=1
        elif score2== "3.3 LOW":
            cvss2=1
        elif score2== "3.2 LOW":
            cvss2=1
        elif score2== "3.1 LOW":
            cvss2=1
        elif score2== "3.0 LOW":
            cvss2=1
        elif score2== "2.9 LOW":
            cvss2=1
        elif score2== "2.8 LOW":
            cvss2=1
        elif score2== "2.7 LOW":
            cvss2=1
        elif score2== "2.6 LOW":
            cvss2=1
        elif score2== "2.5 LOW":
            cvss2=1
        elif score2== "2.4 LOW":
            cvss2=1
        elif score2== "2.3 LOW":
            cvss2=1
        elif score2== "2.2 LOW":
            cvss2=1
        elif score2== "2.1 LOW":
            cvss2=1
        elif score2== "2.0 LOW":
            cvss2=1
        elif score2== "1.9 LOW":
            cvss2=1
        elif score2== "1.8 LOW":
            cvss2=1
        elif score2== "1.7 LOW":
            cvss2=1
        elif score2== "1.6 LOW":
            cvss2=1
        elif score2== "1.5 LOW":
            cvss2=1
        elif score2== "1.4 LOW":
            cvss2=1
        elif score2== "1.3 LOW":
            cvss2=1
        elif score2== "1.2 LOW":
            cvss2=1
        elif score2== "1.1 LOW":
            cvss2=1
        elif score2== "1.0 LOW":
            cvss2=1
        elif score2== "0.9 LOW":
            cvss2=1
        elif score2== "0.8 LOW":
            cvss2=1
        elif score2== "0.7 LOW":
            cvss2=1
        elif score2== "0.6 LOW":
            cvss2=1
        elif score2== "0.5 LOW":
            cvss2=1
        elif score2== "0.4 LOW":
            cvss2=1
        elif score2== "0.3 LOW":
            cvss2=1
        elif score2== "0.2 LOW":
            cvss2=1
        elif score2== "0.1 LOW":
            cvss2=1

    if exploit == "Being Exploited":
        exp=5
    else:
        exp=0

    snooper_score = exp + cvss3 + cvss2 + goog

    if snooper_score < 5:
        rep="Score is less than 5, this CVE wouldn't be a major issue, whoever if being exploited: action is recomended."
    elif snooper_score >= 5 and snooper_score <= 10:
        rep="Score is below 10, use caution when dealing with this CVE as it could pose a problem in the future."
    elif snooper_score >= 11 and snooper_score <= 15:
        rep="Score is between 10 and 15, the CVE needs to be addressed and fixed for the system in question."
    elif snooper_score >= 16:
        rep="Score is over 15, drop everything you are doing and make sure this CVE is fixed if it applies to your systems."

    return render_template('scoring.html', id=cve_id, summary=summary, cvss3_score=score3,match=key_match, cvss2_score=score2, url=cve_url, google=google, exploit=exploit, snooper_score=snooper_score, res=rep)



if __name__ == '__main__':
    app.run(debug=True)