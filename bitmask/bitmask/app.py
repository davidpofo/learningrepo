# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session, Session
import json
import sys
import os
from urllib.request import urlopen


app = Flask(__name__)


# ======== Routing =========================================================== #

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if session.get('logged_in'):
        user = helpers.get_user()
        wallets = helpers.get_wallets()

        if request.method == 'POST':
            id = request.form['id']
            helpers.remove_wallet(id)
            return redirect(url_for('homepage'))
        return render_template('home.html', user=user, wallets=wallets)
    return redirect(url_for('login'))


@app.route('/d/<url>/', methods=['GET'])
def donation(url):
    wallet = helpers.get_wallet(url)
    try:
        amount = request.args["amount"]
    except:
        amount = None

    try:
        address = request.args["address"]
    except:
        address = None

    if amount != None and address == None:
        address = helpers.get_address(wallet)
        if address:
            return redirect("/d/" + url + "/?amount=" + amount + "&address=" + address)

    if amount != None and address != None:
        page = urlopen("https://blockchain.info/ticker")
        contents = page.read()
        btc = float(amount)/float(json.loads(contents.decode('utf-8'))["USD"]["15m"])
        if btc:
            link = "bitcoin:" + address + "?amount=" + str(btc)
            return render_template('donation.html', wallet=wallet, btc=round(btc, 8), address=address, link=link)

    return render_template('donation.html', wallet=wallet)


@app.route('/support', methods=['GET'])
def support():
    return render_template('support.html')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if session.get('logged_in'):
        if request.method == 'POST':
            title = request.form['title']
            key = request.form['mpk']
            if title != "" and key != "":
                if(helpers.add_key(title, key)):
                    return redirect(url_for('homepage'))
                return render_template('add.html', error="Invalid key")
            return render_template('add.html', error="Title and key required")
        return render_template('add.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if username != "" and password != "":
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return redirect(url_for('homepage'))
                return render_template('login.html', error="Invalid username or password.")
            return render_template('login.html', error="Fill in both fields.")
        return render_template('login.html', form=form)
    return redirect(url_for('homepage'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            if form.validate():
                if request.form['password'] == request.form['cpassword']:
                    if not helpers.username_taken(username):
                        helpers.add_user(username, password)
                        session['logged_in'] = True
                        session['username'] = username
                        return redirect(url_for('homepage'))
                    return render_template('register.html', error="Username Taken")
                return render_template('register.html', error="Passwords do not match")
            return render_template('register.html', error="User/Pass Required")
        return render_template('register.html', form=form)
    return redirect(url_for('homepage'))


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            helpers.change_user(password=password)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.secret_key = os.urandom(12)  # Generic key for dev purposes only
    app.run(debug=True, use_reloader=True)
