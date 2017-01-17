# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests,random,time
import pymongo
import traceback
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.setrecursionlimit(50000)
import string

client = pymongo.MongoClient('localhost', 27017,connect=False)
DouBanMovie = client['DouBanMovie']
GreatWallComment = DouBanMovie['GreatWallComment']
GreatWallComment2 = DouBanMovie['GreatWallComment2']

def get_soup(url):

    time.sleep(0)

    my_headers =['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.'
                 '0.2227.1 Safari/537.36',
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36' ,
                 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.'
                 '2062.124 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0'
                 '.2049.0 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'

                 ]

    headers = {"User-Agent": random.choice(my_headers),
               "Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11)) +
                        ';'
               }

    html = requests.get(url,headers = headers,timeout = 6)
    soup = BeautifulSoup(html.text,'lxml')

    return soup

def get_comment(start_url):

    try:
        soup = get_soup(start_url)
        #print soup
        if not soup:
            print ('soup is empty')
            return
        #print soup

        comments = soup.find_all("div", class_ = "comment-item")
        #print (soup.find_all("div", class_ = "comment-item"))

        for comment in comments:
            #print comment
            if comment.find('span',class_ = 'rating') == None:
                comment_data = {'comment_info': comment.find('a').get("title"),
                                'rating': '',
                                'comment_time': comment.find('span', class_='comment-time').get_text(),
                                'comment_vote': comment.find('span', class_='pr5').get_text(),
                                'comment': comment.find('p').get_text()

                                }
            else:
                comment_data = { 'comment_info' : comment.find('a').get("title"),
                                 'rating': comment.find('span',class_ = 'rating').get('title'),
                                 'comment_time' : comment.find('span',class_= 'comment-time').get_text(),
                                 'comment_vote' : comment.find('span',class_ = 'pr5').get_text(),
                                 'comment' : comment.find('p').get_text()

                               }

            if GreatWallComment.find(comment_data).count() == 0:
                GreatWallComment.insert_one(comment_data)
            else:
                pass

        next_url = start_url.split('?',1)[0] + soup.find_all("a",class_ = "next")[0].get('href')\
            .replace('&amp;','').strip()
        print (next_url)

        if next_url is not start_url.split('?',1)[0]:

            get_comment(start_url = next_url)

        else:
            print ('done')

    except IndexError:
        traceback.print_exc()
        soup = get_soup(start_url)
        print soup.find("div", class_="center")
        print soup.find("div", class_="center").find_all('a')[1].get('href')
        next_url = start_url.split('?', 1)[0] + soup.find("div", class_="center").find_all('a')[1].get('href')\
            .replace('&amp;','').strip()
        print next_url
        get_comment(start_url= next_url)

    except :
        soup = get_soup(start_url)
        next_url = start_url.split('?', 1)[0] + soup.find_all("a", class_="next")[0].get('href')\
            .replace('&amp;','').strip()
        get_comment(start_url = next_url)



def get_comment_2(start_url):

    try:
        print start_url
        soup = get_soup(start_url)
        if not soup:
            print ('soup is empty')
            return
        print soup

        comments = soup.find_all("div",id = "comment-list")
        print comments

        for comment in comments:

            comment_data = { 'comment_info' : comment.find("strong").get_text(),
                             'rating': comment.find("span",class_ = "rating-stars").get('data-rating'),
                             'comment_time' : comment.find("div",class_= "date").get_text(),
                             'comment_vote' : comment.find("span",class_ = "text").get_text(),
                             'comment' : comment.find('p').get_text()

                           }

            print json.dumps(comment_data, encoding="UTF-8", ensure_ascii=False)

            if GreatWallComment.find(comment_data).count() == 0:
                GreatWallComment.insert_one(comment_data)
            else:
                pass

    except:
        traceback.print_exc()
        print start_url


if __name__ == '__main__':

    start_url = 'https://movie.douban.com/subject/6982558/comments?start=107845&limit=20&sort=time&status=P'
    get_comment(start_url = start_url)
