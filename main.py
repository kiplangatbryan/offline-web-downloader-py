from importlib.resources import path
from logging import error, exception
from msilib.schema import Error
import sys
from urllib import response
from xml.dom.pulldom import ErrorHandler
from aiohttp import request
from pip import main
import requests
from bs4 import BeautifulSoup
import os
import pathlib

class Scraper:
    def __init__(self, url):
        '''
        Accepts url of target website e.g example.com
        '''
        self.main_url  = url
        self.config  = { "a": 'href', "script": "src", "link": "href", "img": "src" }
        


    def fetch_html(self) -> response:
        try:
            res = requests.get(self.main_url)
            return res
        except exception as e: 
            print(f'There was a problem accessing page {e}')
            sys.exit(1)


    def generateSoup(self,res) -> BeautifulSoup:
        '''
        process the raw html BeautifulSoup Object
        '''
        return BeautifulSoup(res, 'lxml')

    def find_links(self, soup):
        '''
        Find all <a> tags, <script> tags, <link> tags, <img> tags 
        '''
        surface_urls = soup.find_all('a')
        surface_scripts = soup.find_all('script')
        surface_links = soup.find_all('link')
        surface_imgs = soup.find_all('img')


        self.urls, self.scripts, self.css_links, self.imgs = self.process_assets(a=surface_urls, script=surface_scripts, link=surface_links, img=surface_imgs)

    def consume_url(self):
        data = [*self.urls,*self.scripts, *self.css_links, *self.imgs]
        # create dirs
        for url in data:
            self.createDirs(url)


    def Extract_dirname_and_create_from_url(self):
        main_dir_name = str.split(str.split(self.main_url, "//")[1], '/')[0]
        self.root_folder = 'assets'

        # if containe a port number del
        if len(main_dir_name.split(':')) > 1:
            main_dir_name = main_dir_name.split(':')[0]


        # create root dir
        main_path = os.path.join(os.getcwd(), self.root_folder, main_dir_name)
    
        if not os.path.exists(main_path):
            os.mkdir(main_path)
            # download index.html file
            self.download_file(os.path.join(main_path), self.main_url)
        self.rootPath  = main_path

        

    def tag_parser(self, soupArr, tag) -> list:
        data = []
        for soup in soupArr:
            # sanitize the string
            url = soup.get(tag)
            # for links
        
            if url == "#" or url == None:
                continue
            if str(url).startswith('./'):
                url =  url.lstrip('./')
            if str(url).startswith('/'):
                url =  url.lstrip('/')

            data.append(url)
        return data

    def process_assets(self, **kwargs):
        '''
        arrange the data
        '''
        urls, scripts, links, imgs = [], [], [], []

        for key, value in kwargs.items():
            if key == 'a':
                urls = self.tag_parser(value, self.config[key])
            if key == 'script':
                scripts = self.tag_parser(value, self.config[key])
            if key == 'img':
                imgs = self.tag_parser(value, self.config[key])
            if key == 'link':
                links = self.tag_parser(value, self.config[key])

        return (
            urls,
            scripts,
            links,
            imgs
        )


    def createDirs(self, url):
        '''
        create directorites for offline web to reside
        '''
        fmt_path = os.path.sep.join(url.lstrip('/').split('/'))

        self.Extract_dirname_and_create_from_url()
        fatal_path = os.path.join(self.rootPath, fmt_path)

        # create directories
        if not os.path.exists(os.path.dirname(fatal_path)):
            os.makedirs(os.path.dirname(fatal_path))
        # extract filename

        # self.download_file(fatal_path, url)

    def error(self, msg):
        raise Error('ConnectionError', msg)

    def download_file(self, path_to_file, url=''):
        '''
        download individual binary file
        '''
        # download the main html file
        try:
            print(path_to_file)
            res  = requests.get(os.path.join(self.main_url,url), stream=True)

            with open(path_to_file, 'wb+') as file_open:
                for chunk in res.iter_content(1024):
                    file_open.write(chunk)  


        except exception as e:
            print(f'unable to locate resource {e}')
        

    def exec(self):
        '''
        initialize the html miner
        '''
        respose_object = self.fetch_html()
        soup = self.generateSoup(respose_object.text)
        self.find_links(soup)

        # start processing
        self.consume_url()


if __name__  == "__main__":
    # process args
    # if link ends with .html just the page
    # extract the dirs 
    # 1. process links that start with /
    if len(sys.argv) > 1:
        print(sys.argv)
        try:
            Scraper(sys.argv[1]).exec()
        except exception as e:
            print(f'There was a problem {e}')
    else:
        print('Insufficient parameters: ):\n Required format: script_path [target_url]')


# PROBLEMS
# prevent duplicate work [make it optional]
# recussion depth [take it as an argument]
