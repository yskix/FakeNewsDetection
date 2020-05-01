from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import pickle, os
from LDA_Inference import inference
    
def save_data_to_pickle(outfile, all_tweets):
    with open(outfile, 'wb') as fp:
        pickle.dump(all_tweets, fp)
        
def read_data_from_pickle(infile):
    with open (infile, 'rb') as fp:
        return pickle.load(fp)

existing_articles = []
if os.path.isfile('./data/all_who_articles'):
    existing_articles = read_data_from_pickle('./data/all_who_articles')
existing_article_links = [article['link'] for article in existing_articles]

links = []
browser = webdriver.Firefox(executable_path = './geckodriver')
for j in range(1,21):
    browser.get('https://www.who.int/news-room/releases/'+str(j))
    soup = BeautifulSoup(browser.page_source, "html.parser")
    # print(j)
    sleep(1)
    for i in soup.find_all('a',class_ = 'link-container'):
        a = i.get('href')
        links.append('https://www.who.int'+ a)
        
new_dict = {new_list: [] for new_list in links if 'confirmsubscription' not in new_list and new_list not in existing_article_links}

for link in new_dict:
    browser.get(link)
    sleep(1)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    article = soup.find('article')
    
    if article:
        paras = article.find_all('p')
    else:
        paras = soup.find_all('p')
    
    if len(paras) > 1:
        temp = []
        for para in paras:
            temp.append(para.get_text())
    else:
        if article:
            div_paras = article.find_all('div')
        else:
            div_paras = soup.find_all('div')
        temp = []
        for para in div_paras:
            temp.append(para.get_text())
            
    topics = []
    for para in temp:
        topics, names = inference(para)
        topics.append(topics)
    topics = [x for x in topics if len(x) != 30]
    topics = sorted([x for y in topics for x in y], key=lambda z:z[1], reverse=True)[0:3]
    existing_articles.append({'link':link, 'text':temp, 'topic':topics})
    
save_data_to_pickle('./data/all_who_articles', existing_articles)