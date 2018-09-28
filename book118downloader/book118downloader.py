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

from urllib import request
from urllib import parse
import json
import pdb
import os
import sys
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pdfgenerator import transfer_images_to_pdf

def crawl_data(browser, url, btn_id, filepath, page_limit=1000):
    # open the url
    browser.get(url)
    # find the "full view" 
    pdf_btn = browser.find_element_by_id(btn_id)
    pdf_btn.click()
    # get base url
    src = browser.find_element_by_id('layer_view_iframe').get_attribute('src')
    host = parse.urlsplit(src).netloc
    # turn to iframe
    browser.switch_to.frame("layer_view_iframe")
    # get total page number
    page_number = int(browser.find_element_by_id('pagecount').text)
    # all paths
    all_page_paths = []
    # get urls of first three pages 
    page_url = browser.find_element_by_xpath("//div[@id='" + 'p1' + "']/img").get_attribute('src')
    all_page_paths.append(page_url)
    page_name = parse.urlsplit(page_url).query[4:]

    # find the key elements
    ids = [('f','Url'),('isMobile','IsMobi'),('isNet','IsNet'),('readLimit','ReadLimit'),('furl','Furl')]
    get_dict = get_values_by_ids(browser, ids)
    get_dict['img'] = page_name
    
    threads = []
    pages_processed = 0
    info_prompt = show_info('Downloading the pages')
    page_limit = min(page_number, page_limit)
    current_page = 0

    def download_page_multithread(clean_all_paths=False, max_threads=10):
        nonlocal pages_processed
        nonlocal current_page
        while threads or all_page_paths:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
                    pages_processed += 1
                    info_prompt(pages_processed, page_limit)
            while len(threads) < max_threads and all_page_paths:
                page_url = all_page_paths.pop(0)
                current_page += 1
                thread = threading.Thread(target=save_page,args=(page_url, current_page, filepath))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            # just run one time
            if not clean_all_paths:
                break

    for i in range(len(all_page_paths) + 1, page_limit + 1):
        request_url = 'https://' + host + '/pdf/GetNextPage/?' + parse.urlencode(get_dict)
        # get page url and page count
        page_name, page_count = get_page_path(request_url) 
        page_url = 'https://' + host + '/img/?img=' + page_name
        all_page_paths.append(page_url)
        download_page_multithread()
        # update img the the current name of page
        get_dict['img'] = page_name

    download_page_multithread(clean_all_paths=True)

    # back the main content
    browser.switch_to.default_content()
    browser.close()
    
def get_values_by_ids(browser, ids):
    get_dict = {}
    for key,value in ids:
        get_dict[key] = browser.find_element_by_id(value).get_attribute('value')
    return get_dict

def get_page_path(request_url):
    try:
        response = request.urlopen(request_url).read().decode('utf-8')
    except Exception as ex:
        raise ex
    else:
        data = json.loads(response)
        return data['NextPage'],data['PageIndex']
 
def save_page(page_url, page_count, filepath):
    equip_num = lambda x:'%04d'%(x)
    try:
        data = request.urlopen(page_url).read()
        with open(os.path.join(filepath, equip_num(page_count)), 'wb') as f:
            f.write(data)
    except Exception as ex:
        raise ex

def show_info(start_info):
    print(start_info, end=':')
    current_char = '/'
    progress_chars = {'-':'\\','\\':'|','|':'/','/':'-'}
    def show_process(current_number, total_number):
        nonlocal current_char
        char_output = current_char + str(current_number) + '/' + str(total_number)
        sys.stdout.write(char_output)
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b' * len(char_output))
        current_char = progress_chars[current_char]
    return show_process

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:python book118_link pdf_filename')
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
        crawl_data(browser, url, btn_id, cache_path)
        print()
        transfer_images_to_pdf(cache_path, sys.argv[2])
    except Exception as ex:
        #pdb.set_trace()
        browser.close()
        raise ex
    finally:
        # delete the cache folder
        import shutil
        shutil.rmtree(cache_path)
