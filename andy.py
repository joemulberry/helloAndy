

# ------- import basic scraping tools -------- #
from bs4 import BeautifulSoup
from random import choice 
import requests 

# ------- undected scrap for Transfermarkt -------- #
def get_souped_page(page_url):
    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'},
        {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    ]
    headers = choice(headers_list)
    pageTree = requests.get(page_url, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')
    return(pageSoup)

# ------- playground -------- #

url = 'https://www.transfermarkt.co.uk/jude-bellingham/profil/spieler/581678'
soup = get_souped_page(url)

# create a store for the data we scrap 
store = {}

# get the players name 
header = soup.find('h1')
raw_text = header.get_text(separator='\n', strip=True) if header else ''
name = raw_text
print('-'*20)
print(name) 
print('-'*20)

store['name'] = name


# print the store 
print(store)
