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
                "Accept-Language": "en-US,en;q=0.8",
                "Cache-Control": "max-age=0",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
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

WIKI_URL = 'https://en.wikipedia.org/w/api.php'
WIKI_PARAMS = {
    "action": "parse",
    "page": None,
    "format": "json",
    "prop": "wikitext",
    "section": 1
}

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
        wiki page name - the movie's wikipedia page's name
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
            return url.split('/')[-1]
    return None

def browse_wiki(page_name):
    '''
    this function will browse the wikipedia page at `url` and retrieve the 'plot'
    section of this movie
    params:
        url - url to a wikipedia page of a movie
    return value:
        a string, the 'plot' section of this page, hopefully it is the first section
        of every wikipage, as set in `PARAMS`
    '''
    params = WIKI_PARAMS
    params['page'] = page_name
    session = requests.Session()
    js = session.get(url=WIKI_URL, params=params)
    raw_data = js.json()
    return raw_data['parse']['wikitext']['*']

