import mechanicalsoup
from httpx import AsyncClient
import sqlite3
import hashlib
import library
import pathlib
import asyncio
from bs4 import BeautifulSoup as bs


debug = True

if debug:
    import personal_info as config
else:
    import config


storage = pathlib.Path(config.storage_path,'sexting pics')
storage.mkdir(parents=True,exist_ok=True)
pages = []

class Page:
    def __init__(self,response,link):
        self.urls=[link]
        _soup = bs(response.content, 'lxml')
        _pages = (_soup.find_all('a', attrs={"class":"page-numbers"}))
        if len(_pages) > 0:
            for page in _pages:
                self.urls.append(page['href'])






def get_area_codes():
    browser = mechanicalsoup.StatefulBrowser(soup_config={'features':'lxml'}, user_agent = config.user_agent)
    browser.open(library.urls.get('home'))
    dropdown = browser.page.find('select', attrs={"name":"taxonomy_dropdown_widget_dropdown_4"}).find_all('option')
    dropdown = [x['value'] for x in dropdown if '?tag' in x['value']]
    return dropdown

async def get_pages(links):
    headers = {'user-agent': config.user_agent}
    async with AsyncClient(http2=True,headers = headers) as c:
        for link in links:
            r = await c.get(link)
            _ = Page(r,link)
            pages.append(_)




async def download():
    with AsyncClient() as c:
        pass

async def check_for_duplicate(file):
    pass



def go():
    links = get_area_codes()
    asyncio.run(get_pages(links))





if __name__ == "__main__":
    go()