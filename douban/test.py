#! /usr/bin/python3
# -*- coding:utf-8 -*-
# author：Sirius.Zhao
import json
import random
import re
import sys
import time
from imp import reload
from urllib.request import Request
from urllib.request import urlopen
import pymysql
from bs4 import BeautifulSoup

from douban.settings import USER_AGENT
from douban.utils import RedisManager
from douban.enums import RedisKeyEnum


def LoadUserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1 - 1])
    random.shuffle(uas)
    return uas


uas = USER_AGENT

# s = {}
# for i in range(3):
#     s["key"] = [1,i,]
#     print(s)
# print(s)
# 所有的电影，去重
dict_movies = {}


def datetime_to_timestamp_in_milliseconds(d):
    def current_milli_time(): return int(round(time.time() * 1000))

    return current_milli_time()


reload(sys)

# 通过下面的网址获取分类列表
# https://movie.douban.com/chart
# 根据分类和比例获取相应的电影
# https://movie.douban.com/typerank?type_name=%E5%96%9C%E5%89%A7&type=24&interval_id=100:90
# 定义一个比例的列表
percent_list = ['100:90', '90:80', '80:70', '70:60', '60:50', '50:40', '40:30', '30:20', '20:10', '10:0']


# 获取分类列表
def find_iterm(url):
    response = urlopen(url)
    bs = BeautifulSoup(response, 'html.parser')
    iterms = bs.select('div.types span a')
    iterms_href = [iterm.get('href') for iterm in iterms]
    iterms_list = [iterm.text for iterm in iterms]
    return iterms_list, iterms_href


# Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
# Accept-Encoding:gzip, deflate, br
# Accept-Language:zh-CN,zh;q=0.9
# Connection:keep-alive
# Cookie:bid=mMrd75oQWFA; __utmc=30149280; __utmc=223695111; __yadk_uid=TsnvvnzAl9l5hXsJExLg5PkZQD8tW2xu; ll="108288"; _vwo_uuid_v2=DA5ED1377260F937BEC8CBD3785E44E53|98ebf520a520de4c9c6b9bed6d211cd7; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1522309082%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DR23_MHR8K3SFj2J4gH-0n2G67VhfRtaG8GFHstysqjnPZ_HxqpDmGX54pQSSCCCd%26wd%3D%26eqid%3Dde9da0fa00002a7f000000035abc9802%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.65574578.1521358273.1522244587.1522309083.7; __utmz=30149280.1522309083.7.7.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.505210566.1522198584.1522244587.1522309083.3; __utmb=223695111.0.10.1522309083; __utmz=223695111.1522309083.3.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; __utmb=30149280.1.10.1522309083; _pk_id.100001.4cf6=c6e6b98e6f177261.1522198584.3.1522309214.1522248302.
# Host:movie.douban.com
# Referer:https://movie.douban.com/chart
# Upgrade-Insecure-Requests:1
# User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36

# 获取某个阶段总的电影数目（100:90....）
def find_total_num(suffix, head):
    link_total = "https://movie.douban.com/j/chart/top_list_count?type=" + suffix
    req = Request(link_total, headers=head)
    total_data = urlopen(req)
    total_num = json.load(total_data)['total']
    return total_num


# 获取电影
# 获取totalNum
# https://movie.douban.com/j/chart/top_list_count?type=24&interval_id=100:90
# {"playable_count":232,"total":431,"unwatched_count":431}
# 获取电影信息
# https://movie.douban.com/j/chart/top_list?type=11&interval_id=100%3A90&start=0&limit=562


def find_allMovie_iterm(type_id, href):
    # print(category, href)
    ua = random.choice(uas)
    head = {
        'User-Agent': ua,
        'Cookie': 'bid=mMrd75oQWFA; __utmc=30149280; __utmc=223695111; __yadk_uid=TsnvvnzAl9l5hXsJExLg5PkZQD8tW2xu; ll="108288"; _vwo_uuid_v2=DA5ED1377260F937BEC8CBD3785E44E53|98ebf520a520de4c9c6b9bed6d211cd7; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1522309082%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DR23_MHR8K3SFj2J4gH-0n2G67VhfRtaG8GFHstysqjnPZ_HxqpDmGX54pQSSCCCd%26wd%3D%26eqid%3Dde9da0fa00002a7f000000035abc9802%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.65574578.1521358273.1522244587.1522309083.7; __utmz=30149280.1522309083.7.7.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.505210566.1522198584.1522244587.1522309083.3; __utmb=223695111.0.10.1522309083; __utmz=223695111.1522309083.3.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; __utmb=30149280.1.10.1522309083; _pk_id.100001.4cf6=c6e6b98e6f177261.1522198584.3.1522309214.1522248302.',
        'Referer': 'https://movie.douban.com/chart'
    }

    # /typerank?type_name=%E5%96%9C%E5%89%A7&type=24&interval_id=
    suffix = href.split('&type=')[1]
    link_movies = "https://movie.douban.com/j/chart/top_list?type=" + suffix

    # 获取数据
    # {
    # "rating":["8.2","45"],
    # "rank":391,
    # "types":["喜剧","犯罪","爱情"],
    # "regions":["美国"],
    # "title":"天堂里的烦恼",
    # "release_date":"1932-10-21",
    # "vote_count":1868,
    # "score":"8.2",
    # "actors":["米利亚姆·霍普金斯","凯·弗朗西斯","赫伯特·马歇尔","查尔斯·拉格尔斯","爱德华·艾沃瑞特·霍顿"],
    # },
    rdc = RedisManager().rdc
    # 去重使用
    for stage in percent_list:
        time.sleep(1)
        suffix_total = suffix + stage
        total = find_total_num(suffix_total, head)
        url_movies = link_movies + stage + '&start=0&limit=6000'
        # 解析每次获取的json串，形成record 考虑去重
        req = Request(url_movies, headers=head)
        movies_list = urlopen(req)
        # 得到一个[{},{},{}]类型的json串
        movies_list = json.load(movies_list)
        print(len(movies_list))
        # print(movies_list)
        # for movie in movies_list[0:1]:
        #     score = movie['score']
        #     vote_count = movie['vote_count']
        #     movie_rank = movie['rank']
        #     cover_url = movie['cover_url']
        #     douban_movie_id = movie['id']
        #     regions = '，'.join(movie['regions'])
        #     title = movie['title']
        #     release_date = movie['release_date']
        #     # actors = '，'.join(movie['actors'])
        #     actor_count = len(movie['actors'])
        #     types = movie['types']
        #     query_type = 'select id from movie_type where type_name=%s;'
        #     ins_sql = 'insert into movie (score, vote_count, movie_rank, cover_url, douban_movie_id, regions, title,' \
        #               ' release_date, actor_count) values (%s,%s,%s,%s,%s,%s,%s,%s,%s);'
        #     execute_dml(ins_sql,score,vote_count,movie_rank,cover_url,douban_movie_id,regions,title,release_date,actor_count)
        # for type in types:
        #     a = execute_query(query_type, type)
        #     print(a)


def execute_query(sql_query, *args):
    con = pymysql.connect(host="localhost", user="root", password="wimness.", database="douban", charset='utf8',
                          port=3306)
    cursor = con.cursor()
    cursor.execute(sql_query, args)
    s = cursor.fetchall()[0][0]
    cursor.close()
    con.close()
    return s


def execute_dml(sql_insert, *args):
    con = pymysql.connect(host="localhost", user="root", password="wimness.", database="douban", charset='utf8',
                          port=3306)
    cursor = con.cursor()
    cursor.execute(sql_insert, args)
    con.commit()
    cursor.close()
    con.close()


def main():
    url = 'https://movie.douban.com/chart'
    # 获取分类列表
    type_list, type_href_list = find_iterm(url)
    # s = 'insert into movie_type (type_name,douban_type_id,count) values (%s,%s,%s);'
    # for i in type_list:
    #     execute_dml(s,i)
    # 获取每个分类的所有的电影 传递：分类，分类href

    for i in range(len(type_href_list)):
        type_id = re.findall('type=(\d+)&interval', type_href_list[i])[0]
        find_allMovie_iterm(type_id, type_href_list[i].split('100:90')[0])


if __name__ == '__main__':
    main()
