
import os
from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import re
from bs4 import BeautifulSoup
import requests
import random
import sqlite3

# SETTING UP

# Setting up the Flask application

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)  # Creates the flask app
app.secret_key='csre'  # secret key in order to use session variables
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')  # set up the SQLAlchemy database connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # initializing db



# initialize object to fill database with (each row contains a Flag )

class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.String(250))
    country = db.Column(db.String(100))

    def __repr__(self):
        return f'<Country {self.id}: {self.country}, {self.flag}>'
    


# DATA SCRAPING

# function that gets the flags data from wikipedia, stores it in a list of tuples and returns it

def web_scraper():
    url = ("https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    images = soup.find_all("img")  # Finding all images on the page (as that's what I need)

    flags_data = []  # list to temporarily store the data
    for img in images:
        if 'Flag' in img['src']:  # every flag image has the word flag in its url
            country = img['alt']
            clean_country = country.split('(')[0].rstrip().replace(" ", "_")
            flag = 'https:' + img['src']
            if clean_country in flag: # This is supposed to keep the data clean - ensuring that the flag is indeed this country's. (but it doesn't work)
                flags_data.append((country, flag)) # adding a tuple that contains a country-flag pair to the list of all data.
    return flags_data


# function that gets the list of tuples with the flag data and inserts it to the database

def insert_data():
    with app.app_context():
        db.session.query(Flag).delete()  # Delete any existing data (because we're reinserting it)
        db.session.commit()
        flags_data = web_scraper()  # getting the data
        for country, flag in flags_data:  # going through each tuple in the list
            Flag_obj = Flag(country=country, flag=flag)  # Creating a new object Flag for each tuple
            db.session.add(Flag_obj)  # Adding the new flag to the db
        db.session.commit()  # Committing the changes (saving the filled db)

        


# GAME LOGIC


# helper function that connects to the database and returns its size

def get_length_of_data():
    conn = sqlite3.connect('database.db')  # creating a connection to the db
    cursor = conn.cursor()
    table_name = 'Flag'
    query = f"SELECT COUNT(*) FROM {table_name}"  # query to get the number of entries in the db
    cursor.execute(query)
    result = cursor.fetchone()  # transforming the query into a tuple
    return result[0]  # returning the first value in the tuple (that's where the result is)


# Function that sets the values for all elements of a round (basically starts a new round)

def set_new_variables(): 
    length_of_data = get_length_of_data() # getting the length of the data
    # Getting a new random Flag object
    choice = random.randint(0, length_of_data)  # getting a random index for the flag-country pair for this round
    chosen_object = Flag.query.get(choice)  # getting the Flag object from the db at the index 'choice'
    
    # Setting the attributes as session variables (to be able to access them in the rest of the app)
    session['flag'] = chosen_object.flag  # setting the flag variable to contain the web_url of the picture of the chosen flag.
    session['correct_country'] = chosen_object.country  # setting the 'correct_country' variable to hold the country name attribute of the chosen flag.
    
    # Creating a list of 5 countries including the chosen one - and setting it as a session variable.
    choices = 5*[None]  # list to store the 5 country choices for the round
    correct_place = random.randint(0,4)  # getting a random location on the board (in the list) to display the correct country
    choices[correct_place] = session['correct_country']   # putting the chosen country's name into the list at the random index 'correct_place'
    for i in range(len(choices)):  # going through the list (in order to fill it up)
        if choices[i] is None:  # avoiding overriding the chosen country
            while True: # loop to choose a random number that's not already in the list
                new_index = random.randint(0, length_of_data)  # choosing a new random number
                new = Flag.query.get_or_404(new_index).country  # Querying the flag object and getting its country attribute.
                if new not in choices:  # avoiding duplicate choices (checks if the new country is in the list - if not, it will loop again and get a new random index)
                    choices[i] = new  # storing the new option (the country name) in the list
                    break  # breaking out of the while loop once a unique value was found
    session['choices'] = choices  # setting the session's 'choices' variable to contain the list of 5 unique countries- including the country of the chosen flag object
    '''
    after running this function we'll have 3 session variables:
    1. flag = flag_url attribute of random flag object
    2. correct_country = country name of (same) random flag object
    3. choices = a list of 5 unique countries - one of them is 'correct_country'
    '''


# ROUTES

@app.route("/", methods=['GET', 'POST'])  # initialize the home page when the app opens for the first time, and when the user presses the 'new round' button
def home():
    set_new_variables()  # creates new (session) variables
    message = "You got this!"
    return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='')

@app.post("/guess")  # after the user submits his guess
def guess():
    try:
        chosen = request.form['chosen_country']  # get the value of the radio button that the user selected (I set the values to be the country name)
    except:  # if the user didn't select a radio button and just pressed submit.
        message = "You didn't choose a country!"
        return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='')

    if chosen == session['correct_country']:  # if the user selected the correct country
        message = "You Win :)"
    else:  # the user selected a different country
        message = "You Lose :( \nThis is " + session['correct_country'] + "'s flag." # displaying the correct country
    return render_template("base.html", flag = session['flag'], countries = session['choices'], message = message, disabled='disabled')  #disabling the guess button (so that the user only gets one chance each round)


if __name__ == "__main__":
    # db.create_all() # - function to create the tables in the db - only need to run this once.
    # insert_data() # - calls the function to fill the db - only run it when you want to update the db.
    app.run(port=5001, debug=True )
