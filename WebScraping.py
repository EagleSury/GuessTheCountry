'''import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

tables = pd.read_html('https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags')
print(len(tables))

print(tables[1]) '''
'''
import requests
page = requests.get('https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags')

print(page.content)

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())
list(soup.children)
print(soup.find_all('a'))'''

import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

flags_dict = {}
for img in soup.find_all('img'):
    if 'Flag' in img['src']:
        country_name = img['alt']
        flag_url = 'https:' + img['src']
        flags_dict[country_name] = flag_url

print(flags_dict)