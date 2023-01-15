import mechanicalsoup
from httpx import AsyncClient
import sqlite3
import hashlib
from datetime import datetime
import library
import pathlib
import asyncio
from bs4 import BeautifulSoup as bs
import piexif
import webbrowser
debug = False
if debug:
    import personal_info as config
else:
    import config
pages = []
database_file = pathlib.Path(config.storage_path,config.database_file_name)
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
                        text_name = "{}.txt".format(file_name.split('.')[0])
                        post_id = soup.find('article')['id']
                        area_code = soup.find('a',attrs={'rel':'tag'}).text
                        cur.execute("SELECT post FROM posts WHERE post=? AND file_name=?",(post_id,file_name))
                        results = []
                        for x in cur.fetchall():
                            for i in x:
                                results.append(i)
                        # if post_id not in results:
                        if True:
                            try:
                                cur.execute("INSERT INTO posts VALUES(?,?,?,?,?)",(post_id,area_code,post_title,file_name,post_datetime))
                                con.commit()
                                with open(pathlib.Path(storage,file_name),'wb') as f:
                                    image = c.open(image_url).content
                                    f.write(image)
                                if config.create_info_files:
                                    with open(pathlib.Path(storage,text_name),'w') as f:
                                        f.write("The file {} was published on {} with the title {}".format(file_name,post_datetime,post_title))
                            except:
                                pass
                    except:
                        pass
def get_area_codes():
    if len(config.area_codes) > 0:
        areas = []
        for area in config.area_codes:
            areas.append(library.urls.get('tag').replace('<area_code>',area))
        return areas
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
con = sqlite3.connect(database_file)
cur = con.cursor()

def run_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS posts(
    post text,
    area_code text,
    title text,
    file_name text,
    published_date text
    
    )""")
    con.commit()
def go():
    run_db()
    links = get_area_codes()
    asyncio.run(get_pages(links))
    con.close()
if __name__ == "__main__":
    if not debug:
        try:
            webbrowser.open(library.urls.get('donations'))
            go()
        except:
            print("Please consider donating at {}".format(library.urls.get('donations')))
            go()
    else:
        go()