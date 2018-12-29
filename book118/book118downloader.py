#!/usr/bin/env python
#coding: utf-8
#Author: Marxlp

"""
Prerequests: python3.x, selenium package in python, webdriver
Installation:
    selenium: >> pip install selenium
    fpdf >> pip install fpdf
    webdriver: https://www.seleniumhq.org/download/
      Mozilla GeckoDriver
      Google Chrome Driver
Usage:
    python  book118downloader book_link name_of_pdf
Notifaction:
    Due the limit of the server in book118.com, the maximum 
    number of pages that can be downloaded was limited to 1000.
"""
from urllib.request import urlopen
from urllib import parse
import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from util.network import save_page, MultiThreadDownloader
    from util.pdfgenerator import transfer_images_to_pdf
else:
    from ..util.network import save_page, MultiThreadDownloader
    from ..util.pdfgenerator import transfer_images_to_pdf

def crawl_data(browser, url, btn_id, filepath, page_limit=1000):
    # open the url
    browser.get(url)
    # find the "full view" 
    pdf_btn = browser.find_element_by_id(btn_id)
    pdf_btn.click()
    # get base url
    src = browser.find_element_by_id('layer_view_iframe').get_attribute('src')
    host = parse.urlsplit(src).netloc
    # get filename
    filename = ''.join(browser.find_element_by_xpath('//*[@id="Preview"]/div[1]/span/h1').text.split(' ')[:-1])
    # turn to iframe
    browser.switch_to.frame("layer_view_iframe")
    # check view type
    try:
        _ = browser.find_element_by_id('ctl')
        type = 'down';
    except Exception:
        type = 'up'
    # get total page number
    if type == 'down':
        page_number = int(browser.find_element_by_id('pagecount').text)
        page_url = browser.find_element_by_xpath("//div[@id='" + 'p1' + "']/img").get_attribute('src')
        page_index = 2
    else:
        page_number = int(browser.find_element_by_id('pageCount').text)
        page_url = browser.find_element_by_xpath("//div[@id='" + 'p0' + "']/img").get_attribute('src')
        page_index = 1
    
    page_name = parse.urlsplit(page_url).query[4:-4]
    # find the key elements
    ids = [('f','Url'),('isMobile','IsMobi'),('isNet','IsNet'),('readLimit','ReadLimit'),('furl','Furl')]
    if type == 'up':
        ids.pop(2)
    get_dict = get_values_by_ids(browser, ids)
    get_dict['img'] = page_name
    page_limit = min(page_number, page_limit)
    
    downloader = MultiThreadDownloader(page_limit, filepath, save_page)
    downloader.add_urls(page_url)
    for i in range(downloader.get_urls_number() + 1, page_limit + 1):
        if type == 'down':
            request_url = 'https://' + host + '/pdf/GetNextPage/?' + parse.urlencode(get_dict)
        else:
            get_dict['sn'] = page_index
            request_url = 'https://' + host + '/PW/GetPage?' + parse.urlencode(get_dict)
        # get page url and page count
        page_name, page_index = get_page_path(request_url) 
        page_url = 'https://' + host + '/img/?img=' + page_name
        downloader.add_urls(page_url)
        downloader.download_link_multithread()
        # update img the the current name of page
        get_dict['img'] = page_name

    downloader.download_link_multithread(clean_all_paths=True)

    # back the main content
    browser.switch_to.default_content()
    browser.close()
    return filename
    
def get_values_by_ids(browser, ids):
    get_dict = {}
    for key,value in ids:
        get_dict[key] = browser.find_element_by_id(value).get_attribute('value')
    return get_dict

def get_page_path(request_url):
    try:
        response = urlopen(request_url).read().decode('utf-8')
    except Exception as ex:
        raise ex
    else:
        data = json.loads(response)
        return data['NextPage'],data['PageIndex']


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:python book118downloader.py book118_link [filename]')
        sys.exit(1)
    # folder to store the pics
    cache_path = '_temp'
    while True:
        if os.path.exists(cache_path):
            cache_path = cache_path + '_'
        else:
            break
    os.makedirs(cache_path)

    url = sys.argv[1]
    btn_id = 'full'
    try:
        # not use gui and disable gpu to speed the process
        browser_options = Options()
        browser_options.add_argument('--headless')
        browser_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=browser_options)
        filename = crawl_data(browser, url, btn_id, cache_path)
        if len(sys.argv) > 2:
            transfer_images_to_pdf(cache_path, sys.argv[2])
        else:
            transfer_images_to_pdf(cache_path, filename)
    except Exception as ex:
        browser.close()
        raise ex
    finally:
        # delete the cache folder
        import shutil
        shutil.rmtree(cache_path)
