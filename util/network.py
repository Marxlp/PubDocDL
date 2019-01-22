# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 01:50:19 2018

@author: Administrator
"""
import os
import sys
import time
import socket
import ssl
from urllib.request import urlopen
import threading

def get_headers(host, uri, headers, port=80, method="GET", use_ssl=False, timeout=100):
    conn = None
    headers = "%s %s HTTP/1.1\r\nHost: %s\r\n"%(method, uri, host) + \
        '\r\n'.join([k+": "+v for k,v in headers.items()]) + "\r\n\r\n"
    print(headers)
    headers = headers.encode()
    if use_ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = ssl_context.wrap_socket(_socket, server_hostname=host)
        conn.connect((host, port))
        conn.send(headers)
    else:
        conn = socket.create_connection((host, port), timeout)
        conn.sendall(headers)

    text = ""
    while True:
        if "\r\n\r\n" in text:
            break
        buff = conn.recv(10).decode()
        text += buff
    conn.close()
    return text.split("\r\n\r\n")[0]

def save_page(page_url, page_count, filepath):
    equip_num = lambda x:'%04d'%(x)
    try:
        data = urlopen(page_url).read()
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
        
class MultiThreadDownloader:
    def __init__(self, total_number, filepath, callback):
        self.pages_processed = 0
        self.threads = []
        self.current_number = 0
        self.info_prompt = show_info('Downloading')
        self.filepath = filepath
        self.total_number = total_number
        self.all_page_paths = []
        self.callback = callback

    def download_link_multithread(self, clean_all_paths=False, max_threads=10):
        while self.threads or self.all_page_paths:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
                    self.pages_processed += 1
                    self.info_prompt(self.pages_processed, self.total_number)
            while len(self.threads) < max_threads and self.all_page_paths:
                page_url = self.all_page_paths.pop(0)
                self.current_number += 1
                thread = threading.Thread(target=self.callback, args=(page_url, self.current_number, self.filepath))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
            # just run one time
            if not clean_all_paths:
                break
            
    def add_urls(self, urls):
        if isinstance(urls, str):
            self.all_page_paths.append(urls)
        else:
            self.all_page_paths.extend(urls)
        
    def get_urls_number(self):
        return len(self.all_page_paths)
    
    def restore_download(self, number):
        self.current_number = number
        self.all_pages_paths = self.all_page_paths[number:]
        self.pages_processed = number
