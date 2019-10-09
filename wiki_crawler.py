import requests
import random
import multiprocessing as mp
import pandas as pd
import csv
import logging
from bs4 import BeautifulSoup
from lxml import etree

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

IMDB_URL = 'https://imdb.com/title/'
IMDB_XPATH = ['//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/h1/text()', \
              '//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/h1/span/a/text()']
GOOGLE_SITES = ['https://www.google.com/search?&q=', 'https://www.google.com.hk/search?&q=', \
                'https://www.google.com.sg/search?&q=', 'https://www.google.co.uk/search?&q=', \
                'https://www.google.com.tw/search?&q=', 'https://www.google.com.au/search?&q=']

USER_AGENTS = [{"Accept": "*/*",
               "Accept-Language": "zh,zh-CN,en-US,en;q=0.8",
               "Cache-Control": "max-age=0",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
               "Connection": "keep-alive",
               "Referer": "https://www.google.com/"
               },
               {"Accept": "*/*",
                "Accept-Language": "zh,zh-CN,en-US,en;q=0.8",
                "Cache-Control": "max-age=0",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1",
                "Connection": "keep-alive",
                "Referer": "https://www.google.com/"
               },
               {"Accept": "*/*",
                "Accept-Language": "zh,zh-CN,en-US,en;q=0.8",
                "Cache-Control": "max-age=0",
                "User-Agent": "Mozilla/5.0 (Linux; U; Android 6.0.1; zh-CN; F5121 Build/34.0.A.1.247) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.1.944 Mobile Safari/537.36",
                "Connection": "keep-alive",
                "Referer": "https://www.google.com/"
               }
               ]

def browse_imdb(id):
    '''
    this function will browse the imdb page for movie with ID `id`,
    and obtain its name and release date
    params:
        id - the IMDb primary key of a specific movie
    return value:
        id - same as input
        name - `movie_name`        
    '''
    imdb_url = IMDB_URL + id
    request = requests.get(imdb_url)
    tree = etree.HTML(request.text)
    name = tree.xpath(IMDB_XPATH[0])[0].strip()
    return id, name

def batch_browse_imdb(ids):
    '''
    this function will run `browse_imdb` on `ids`, a list of IDs
    params:
        ids - a list of IDs
    return value:
        ids_names - a dict, key is IMDb ID, value is `movie_name<space>release_year` 
    '''
    with mp.Pool() as pool:
        results = pool.map(browse_imdb, ids)
    
    ids_names = dict()
    for result in results:
        ids_names[result[0]] = result[1]
    
    return ids_names

def search_google(query):
    '''
    this function will google `query`, and find the wikipedia page of this movie
    params:
        query - movie name
    return value:
        wiki_url - wikipedia page of this movie
    '''
    google_prefix = random.choice(GOOGLE_SITES)
    google_url = google_prefix + query
    header = random.choice(USER_AGENTS)
    
    try:
        page = requests.get(url=google_url, headers=header).text
    except Exception as e:
        logger.error('Exception {} occurs in search'.format(e), exc_info=True)
        if google_prefix != GOOGLE_SITES[0]:
            page = requests.get(url=GOOGLE_SITES[0]+query, headers=header).text
        else:
            return None

    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        print(url)
        if url and 'en.wikipedia.org' in url:
            return url
    return None

def browse_wiki(url):
    '''
    this function will browse the wikipedia page at `url` and retrieve the 'plot'
    section of this movie
    params:
        url - url to a wikipedia page of a movie
    return value:
        plot - a string, the 'plot' section of this page
    '''
    header = random.choice(USER_AGENTS)
    page = requests.get(url, headers=header).text
    # TODO wikipedia seems to have an API for getting a specific section of a page

