#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:17:37 2020

@author: rabeet
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import json

with open('who_scrap2.json', 'r') as f:
    articles = json.load(f)

links = []
browser = webdriver.Firefox(executable_path = '/home/rabeet/Downloads/geckodriver')
for j in range(1,21):
    page = browser.get('https://www.who.int/news-room/releases/'+str(j))
    soup = BeautifulSoup(page.page_source, "html.parser")
    # print(j)
    sleep(1)
    for i in soup.find_all('a',class_ = 'link-container'):
        a = i.get('href')
        links.append('https://www.who.int'+ a)
        
new_dict = {new_list: [] for new_list in links if 'confirmsubscription' not in new_list and new_list not in articles}

# articles = {}
for link in new_dict:
    page = browser.get(link)
    sleep(1)
    soup = BeautifulSoup(page.page_source, 'html.parser')
    
    article = soup.find('article')
    
    if article:
        paras = article.find_all('p')
    else:
        paras = soup.find_all('p')
    
    # paras = article.find_all('p')
    if len(paras) > 1:
        temp = []
        for para in paras:
            temp.append(para.get_text())
        articles[link] = temp
    else:
        if article:
            div_paras = article.find_all('div')
        else:
            div_paras = soup.find_all('div')
        temp = []
        for para in div_paras:
            temp.append(para.get_text())
        articles[link] = temp        

json_object = json.dumps(articles)
with open('who_scrap2.json', 'w') as f:
    f.write(json_object)