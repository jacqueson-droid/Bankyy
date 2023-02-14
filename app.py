
from flask import Flask, flash, render_template, request, redirect, url_for, session,g
from flask_login import login_required
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

import time
import datetime
import MySQLdb.cursors
import re
import random
import string

app = Flask(__name__)

app.secret_key = 'TIGER'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bank'

mysql = MySQL(app)
ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


@app.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM customers")

    data1 = cursor.fetchall()

    return render_template('index.html', data=data1)

@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:            
            if user['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                mesage = 'Logged in successfully !'
                return redirect(url_for('users'))
            else:
               mesage = 'Only admin can login' 
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

  
  
@app.route('/register-user', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country = request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES ( % s, % s, % s, % s, % s)', (userName, email, password, role, country))
            mysql.connection.commit()
            mesage = 'New user created!'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)

  
@app.route("/users", methods =['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()    
        return render_template("users.html", users = users)
    return redirect(url_for('login'))
    


@app.route("/edit", methods =['GET', 'POST'])
def edit():
    msg = ''    
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (editUserId, ))
        editUser = cursor.fetchone()
        if request.method == 'POST' and 'name' in request.form and 'userid' in request.form and 'role' in request.form and 'country' in request.form :
            userName = request.form['name']   
            role = request.form['role']
            country = request.form['country']            
            userId = request.form['userid']
            if not re.match(r'[A-Za-z0-9]+', userName):
                msg = 'name must contain only characters and numbers !'
            else:
                cursor.execute('UPDATE user SET  name =% s, role =% s, country =% s WHERE userid =% s', (userName, role, country, (userId, ), ))
                mysql.connection.commit()
                msg = 'User updated !'
                return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'        
        return render_template("edit.html", msg = msg, editUser = editUser)
    return redirect(url_for('login'))


@app.route("/password_change", methods =['GET', 'POST'])
def password_change():
    mesage = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')        
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form  :
            password = request.form['password']   
            confirm_pass = request.form['confirm_pass'] 
            userId = request.form['userid']
            if not password or not confirm_pass:
                mesage = 'Please fill out the form !'
            elif password != confirm_pass:
                mesage = 'Confirm password is not equal!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE user SET  password =% s WHERE userid =% s', (password, (userId, ), ))
                mysql.connection.commit()
                mesage = 'Password updated !'            
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'        
        return render_template("password_change.html", mesage = mesage, changePassUserId = changePassUserId)
    return redirect(url_for('login'))

@app.route("/view", methods =['GET', 'POST'])
def view():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (viewUserId, ))
        user = cursor.fetchone()   
        return render_template("view.html", user = user)
    return redirect(url_for('login'))



# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('userid', None)
#     session.pop('email', None)
#     return redirect(url_for('login'))


@app.route('/transaction', methods=['GET', 'POST'])
def make():
    msg = 'Please enter details to be added'
    if request.method == 'POST' and 'cid' in request.form and 'cname' in request.form and 'cemail' in request.form and 'cbal' in request.form:
        user = request.form['cname']
        id = request.form['cid']
        email = request.form['cemail']
        bal = request.form['cbal']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name,id, accountNumber FROM customers WHERE id=%s", (id,))
        pid = cursor.fetchall()
        return render_template('make.html',value=pid,value1=user,value2=id,value3=email,value4=bal, value5=pid[0][2])



@app.route("/transactions", methods=['GET', 'POST'])
def transact():
    mesage = ''
    if request.method == 'POST' and 'reciever' in request.form and 'amount' in request.form and 'pname' in request.form and 'pbal' in request.form:
        reciever = request.form['reciever']
        amount = float(request.form['amount'])
        amount1 = float(request.form['amount'])
        sender = request.form['pname']
        scurrbal = str(request.form['pbal'])
        saccNo = str(request.form['pacc'])
        cursor = mysql.connection.cursor()
        sbal = scurrbal - amount
        cursor.execute("SELECT curr_bal FROM customers WHERE name=%s", (reciever,))
        rcurr_bal = cursor.fetchone()
        if rcurr_bal is not None:
            rcurrbal = float(rcurr_bal[0])
            rbal = rcurrbal + amount1
            print(rcurrbal)
            print(rbal)
        else:
            print("Receiver not found.")

        cursor.execute("SELECT * FROM transactions WHERE sname=%s", (sender,))

        tid = cursor.fetchall()
        if scurrbal >= amount:
            cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (rbal, reciever,))
            cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (sbal, sender,))
            cursor.execute("INSERT INTO transactions(customerAccNo,sname,rname,transactionType,amount) VALUES ( %s, %s, %s, %s, %s)",
                           (saccNo,sender, reciever, 'Debit' ,amount,))
            mysql.connection.commit()
        else:
            mesage =  "Insufficient Funds!"
            return render_template('make.html', mesage=mesage)
        return redirect(url_for('transhis'))
        #return render_template('tranhis.html',value=tid)


@app.route('/history')
def transhis():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY time DESC')
    data1 = cursor.fetchall()
    return render_template('tranhis.html', data=data1)

#customers routes
@app.route('/user/home')
# @login_required
def customer_homepage():
        return render_template('user/home.html')
  
@app.before_request
def before_request():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)

@app.route('/user/account')
def customer_account():
    customerAccno = session.get('account_num')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM customers where AccountNumber = %s', (customerAccno,))
    data = cursor.fetchall()
    print(data)
    return render_template('user/account.html', data=data )


@app.route('/update_acc', methods =['GET', 'POST'])
def updateacc():
    if request.method == 'POST' and 'firstname' in request.form and 'password' in request.form and 'email' in request.form and 'phoneNumber' in request.form and 'address' in request.form and 'province' in request.form and 'country' in request.form and 'language' in request.form and 'currency' in request.form:
        firstName = request.form['firstname']
        password = request.form['password']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']
        address = request.form['address']
        province = request.form['province']
        country = request.form['country']
        language = request.form['language']
        currency = request.form['currency']

        custAccno = session.get('account_num')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT accountNumber FROM customers where AccountNumber = %s', (custAccno,))
        accountno = cursor.fetchone()
        print(accountno)
        cursor.execute("UPDATE customers SET name=%s, email=%s, password=%s, phonenumber=%s, address=%s, country=%s, province=%s, currency=%s, language=%s WHERE accountNumber=%s", (firstName, email, password, phoneNumber, address, country, province, currency, language, custAccno))
        mysql.connection.commit()
    return redirect(url_for('customer_account'))   

@app.route('/user')
def customer_loginpage():
    return render_template('user/auth.html')

@app.route('/user/transfer')
def customer_transfer():
    return render_template('user/auth.html')


@app.route('/user/transaction-history')
def customer_transhistory():
    customerAcc = session.get('account_num')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT rname FROM transactions where customerAccNo = %s', (customerAcc,))
    cus_rname = cursor.fetchone()
    print(cus_rname)
    cursor.execute('SELECT * FROM transactions where customerAccNo = %s UNION ALL SELECT * FROM transactions where rname = %s ORDER BY time DESC', (customerAcc, cus_rname['rname'] ,))
    data1 = cursor.fetchall()
    print(data1)
    return render_template('user/transaction-history.html', data=data1)



@app.route('/register')
def customer_registerpage():
    return render_template('user/register.html') 

@app.route('/register_me', methods =['GET', 'POST'])
def user_register():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'terms' in request.form :
        userName = request.form['username']
        password = request.form['password']
        email = request.form['email']
        terms = request.form['terms']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            
            alphabet = string.ascii_letters
            numbers = string.digits
            random_string = ''.join(random.choice(alphabet) for i in range(5))
            random_string += ''.join(random.choice(numbers) for i in range(10))
            account_num = ''.join(random.sample(random_string, len(random_string)))

            cursor.execute("INSERT INTO customers (name, email, password, terms, accountNumber) VALUES (%s, %s, %s, %s, %s)", (str(userName), str(email), str(password), str(terms), str(account_num)))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
            session['loggedin'] = True
            session['name'] =  userName
            session['email'] = email
            
            return render_template('user/home.html', mesage = mesage)
    elif request.method == 'POST':
        mesage = 'Please fill out the form !!'
        return render_template('user/register.html', mesage = mesage)
    return render_template('user/register.html', mesage = mesage)


@app.route('/home', methods = ['POST', 'GET'])
def customer_login():
    mesage = ''
    if request.method == 'POST' and 'email_username' in request.form and 'password' in request.form:
        email_username = request.form['email_username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE email = % s AND password = % s', (email_username, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['account_num'] = user['accountNumber']
            mesage = 'Logged in successfully !'

            cursor.execute('SELECT * FROM customers WHERE id = % s ', (session['userid'],))
            cust_info = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*)  FROM transactions WHERE customerAccNo = % s ", (session['account_num'],))
            num_row = cursor.fetchone()
            print(num_row)
            
            return render_template('user/home.html', cust_information = cust_info, result = num_row['COUNT(*)'], mesage = mesage)
            #return redirect(url_for('customer_homepage'))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('user/auth.html', mesage = mesage)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('customer_loginpage'))


#customers routes
@app.route('/staff/home')
@login_required
def staff_homepage():
    return render_template('staff/home.html', segment='index')

@app.route('/staff')
def staff_loginpage():
    return render_template('staff/auth.html', segment='index')


if __name__ == "__main__":
    app.run(debug=True)
