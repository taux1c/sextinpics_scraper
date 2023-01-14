import mechanicalsoup
from httpx import AsyncClient
import sqlite3
import hashlib
import library
import pathlib
import asyncio
from bs4 import BeautifulSoup as bs
from datetime import datetime
import piexif
import dateutil



debug = True

if debug:
    import personal_info as config
else:
    import config
pages = []

class Page:
    def __init__(self,response,link):
        self.urls=[link]
        self.articles = []
        _soup = bs(response.content, 'lxml')
        _pages = (_soup.find_all('a', attrs={"class":"page-numbers"}))
        if len(_pages) > 0:
            for page in _pages:
                self.urls.append(page['href'])
        self.area_code = link.split('?tag=')[-1]
        self.storage = pathlib.Path(config.storage_path, 'sexting pics',self.area_code)
        self.storage.mkdir(parents=True, exist_ok=True)
        self.parse_pages()
        self.process_articles()
    def parse_pages(self):
        with mechanicalsoup.StatefulBrowser(soup_config={'features':'lxml'}, user_agent = config.user_agent) as c:
            for url in self.urls:
                c.open(url)
                self.articles.append(c.page.find_all('article'))

    def process_articles(self):
        with mechanicalsoup.StatefulBrowser(soup_config={'features':'lxml'}, user_agent = config.user_agent) as c:
            for collection in self.articles:
                for article in collection:
                    soup = bs("""{}""".format(article),'lxml')
                    try:
                        image_url = soup.find('img')['src']
                        post_datetime = soup.find('time')['datetime']
                        post_title = soup.find('a',attrs={'rel':'bookmark'}).text
                        storage = self.storage
                        file_name = image_url.split('/')[-1]
                        with open(pathlib.Path(storage,file_name),'wb') as f:
                            image = c.open(image_url).content
                            f.write(image)


                    except:
                        pass



def get_area_codes():
    with mechanicalsoup.StatefulBrowser(soup_config={'features':'lxml'}, user_agent = config.user_agent) as browser:
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


def go():
    links = get_area_codes()
    asyncio.run(get_pages(links))







if __name__ == "__main__":
    go()