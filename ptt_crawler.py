
from sqlalchemy import create_engine
import pymysql
import requests
import re
import time
import pandas as pd
import datetime
from tqdm import tqdm


def crawl_page(url):
    mainUrl = 'https://www.ptt.cc'
    targetUrl = mainUrl+url
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    cookies = {'over18': '1'}  # age over 18
    web = requests.get(targetUrl, headers=headers, cookies=cookies)
    return web.text


def crawl_N_PttPage(url, n):
    # get first page since its url is 'https://www.ptt.cc/bbs/Gossiping/index.html'
    # pattern of html (only crawl those with comments)
    pattern_of_prePage = re.compile(
        'class="btn-group btn-group-paging">\s+<a.*?>.*?<\/a>\s+<a class="btn wide" href=".*?index(.*?).html">')
    pattern_of_articleInfo = re.compile(
        'class="nrec"><s.*?>(.*?)<\/span><\/div>\s+<div class="title">\s+<a href="(.*?)">(.*?)<\/a>\s+<\/div>\s+<d.*?>\s+<d.*?>(.*?)<\/div>\s+<d.*?>\s+<d.*?>.*?<\/div>\s+<d.*?>\s+<d.*?><a.*?>.*?<\/a><\/div>\s+<d.*?><a.*?>.*?<\/a><\/div>\s+<\/div>\s+<\/div>\s+<d.*?>(.*?)<\/div>')
    web = crawl_page(url)  # crawling
    # match text
    pre_Page = re.findall(pattern_of_prePage, web)
    page1_Info = re.findall(pattern_of_articleInfo, web)
    page1_Info = page1_Info[:-4]  # delete notification article
    # get n pages
    page_N_Info = []
    # input n
    for page in tqdm(range(0, int(n)-1)):
        # Using the pre_Page above to crawl earlier pages
        sourceUrl = url[:-5] + str(int(pre_Page[0])-page) + url[-5:]
        web = crawl_page(sourceUrl)
        page_N_Info.append(re.findall(pattern_of_articleInfo, web))
    print('--------- crawl N page done ---------')
    return page1_Info, page_N_Info


def merge_data(page1_Info, page_N_Info):
    push = []  # Number of Push
    title = []  # Article Title
    author = []  # User's account name
    date = []  # Post date
    href = []  # Url of the Article
    for item in page1_Info:
        push.append(item[0])
        title.append(item[2])
        author.append(item[3])
        date.append(item[4])
        href.append(item[1])
    for item in page_N_Info:
        for item in item:
            push.append(item[0])
            title.append(item[2])
            author.append(item[3])
            date.append(item[4])
            href.append(item[1])
    # transfer to DataFrame
    data_article = {'push': push, 'title': title,
                    'author': author, 'date': date, 'href': href}
    data_article = pd.DataFrame(data_article)
    return data_article


url = '/bbs/Gossiping/index.html'
page1_Info, page_N_Info = crawl_N_PttPage(url, 10)
data_article = merge_data(page1_Info, page_N_Info)

# p_sql = password_sql
# db_sql = database_name_sql
engine = create_engine(
    'mysql+pymysql://root:p_sql@localhost:3306/db_sql')
data_article.to_sql('PTT', engine, index=True)
print("Write to MySQL successfully!")
