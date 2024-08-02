import unittest
from app import db, Flag, app

def test_flag_country_consistency():
    with app.app_context():
        flags = Flag.query.all()

    for flag in flags:
        if flag.country not in ['Ivory_Coast', 'São_Tomé_and_Príncipe', 'United_States_of_America']: # Only this image url doesn't have the country's name - I manually checked that the program works if this is the chosen flag (id = 84)
            assert flag.country in flag.flag, f"{flag.country} is not in {flag.flag} "