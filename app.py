
import os
from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import re
from bs4 import BeautifulSoup
import requests
import random
import sqlite3

# setting up the application

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key='csre'
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')  # set up the database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # initializing db



# initialize object to fill database with (each row contains - )
class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.String(250))
    country = db.Column(db.String(100))

    def __repr__(self):
        return f'<Country {self.id}: {self.country}, {self.flag}>'

# function that gets the flags data from wikipedia and stores it in a list of tuples and returns it

def web_scraper():
    url = ("https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    images = soup.find_all("img")

    flags_data = []
    for img in images:
        if 'Flag' in img['src']:
            country = img['alt']
            flag = 'https:' + img['src']
            flags_data.append((country, flag))
    return flags_data

# function that gets the list of tuples with the flag data and inserts it to the database
def insert_data():
    with app.app_context():
        flags_data = web_scraper()
        for country, flag in flags_data:
            Flag = Flag(country=country, flag=flag)
            db.session.add(Flag)
        db.session.commit()

def get_length_of_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    table_name = 'Flag'
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def set_new_variables(): # setting the values for all elements of a round
    length_of_data = get_length_of_data() # db.session.Exec("select count() from flag")
    # line to read in country_flags from sqllite file
    choice = random.randint(0, length_of_data)  # getting a random index for the correct flag-country pair for this round
    correct_place = random.randint(0,4)  # getting a random location on the board to display the correct country
    chosen_object = Flag.query.get(choice)  # setting the flag picture
    session['flag'] = chosen_object.flag
    choices = 5*[None]  # list to store the 5 choices for the round
    session['correct_country'] = chosen_object.country
    choices[correct_place] = session['correct_country']   # setting the random location to equal the chosen country's name
    for i in range(len(choices)):  # going through the list (in order to fill it up)
        if choices[i] is None:  # avoiding overriding the chosen country
            while True: # loop to choose a random number that's not already in the list
                new_index = random.randint(0, length_of_data)  # choosing a new random number
                new = Flag.query.get_or_404(new_index).country
                if new not in choices:  # avoiding duplicate choices
                    choices[i] = new  # storing the new option (the country name) into the list
                    break  # breaking out of the while loop once a unique value was found
    session['choices'] = choices


@app.route("/", methods=['GET', 'POST'])  # initialize the home page
def home():
    set_new_variables()
    message = "You got this!"
    return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='')

@app.post("/guess")  # after the user submits his guess
def guess():
    try:
        chosen = request.form['chosen_country']
    except:
        message = "You didn't choose a country!"
        return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='')

    if chosen == session['correct_country']:
        message = "You Win :)"
    else:
        message = "You Lose :( \nThis is " + session['correct_country'] + "'s flag."
    return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='disabled')


if __name__ == "__main__":
    # db.create_all() - is this a function to create an empty db? what does this do?
    # insert_data() # - calls the function to fill the db - only run it when you want to update the db.
    app.run(debug=True)
