# -*- coding: utf-8 -*-
import json
import re
import scrapy
from douban.enums import RedisKeyEnum, SpiderNameEnum
from douban.items import MovieItem
from douban.utils import RedisManager
from douban.aop import consume_time


class MovieSpider(scrapy.Spider):
    name = SpiderNameEnum.movie.value
    allowed_domains = ['movie.douban.com']
    types = ['剧情', '喜剧', '爱情', '科幻', '动画', '悬疑', '惊悚', '恐怖', '犯罪', '同性', '音乐', '歌舞', '传记',
             '历史', '战争', '西部', '奇幻', '冒险', '灾难', '武侠', '情色']
    formality = ['电影', '电视剧', '综艺', '动漫', '纪录片', '短片']
    start_urls = []
    url = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags={},{}&start=0'
    rate = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rm = RedisManager()
        over_movie_tag_set = self.rm.rdc.smembers(RedisKeyEnum.over_movie_tag_set.value)
        for i in self.types:
            for j in self.formality:
                if '{},{}'.format(j, i) in over_movie_tag_set:
                    continue
                self.start_urls.append(self.url.format(j, i))

    # @consume_time
    def parse(self, response):
        print(response.url)
        movie_jsons = json.loads(response.text)
        if 'data' not in movie_jsons or len(movie_jsons['data']) == 0:
            ks = re.findall('tags=(.*),(.*)&start', s)[0]
            self.rm.rdc.sadd(RedisKeyEnum.over_movie_tag_set.value, ks)
            return
        movie_list = movie_jsons['data']
        for movie in movie_list[0:1]:
            movie_item = MovieItem()
            if 'rate' not in movie or movie['rate'] is '':
                movie_item['score'] = -1
            else:
                movie_item['score'] = movie['rate']
            movie_item['url'] = movie['url']
            movie_item['title'] = movie['title']
            movie_item['directors'] = ','.join(movie['directors'])
            movie_item['actors'] = '，'.join(movie['casts'])
            movie_item['cover_url'] = movie['cover']
            movie_item['douban_movie_id'] = movie['id']
            yield movie_item
        url = response.url
        page_no = int(re.findall('start=(\\d+)', url)[0])
        url = '{}{}'.format(url[:url.index('start=') + 6], page_no + 1)
        yield scrapy.Request(url=url, callback=self.parse)


if __name__ == '__main__':
    s = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=电影,电视剧&start=0'
    r = re.findall('tags=(.*)&start', s)
    print(r)
