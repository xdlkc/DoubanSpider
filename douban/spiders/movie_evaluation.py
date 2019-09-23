# -*- coding: utf-8 -*-
import re

import scrapy

from douban.enums import SpiderNameEnum, RedisKeyEnum
from douban.items import EvaluationItem
from douban.utils import RedisManager


class MovieValuationSpider(scrapy.Spider):
    name = SpiderNameEnum.movie_evaluation.value
    allowed_domains = ['movie.douban.com']
    start_urls = []
    url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&sort=new_score&status=P'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rdc = RedisManager().rdc
        movie_id_set = self.rdc.hkeys(RedisKeyEnum.movie_comment_page_hash_keys.value)
        for douban_movie_id in movie_id_set[1000:]:
            self.start_urls.append(
                self.url.format(douban_movie_id,
                                self.rdc.hget(RedisKeyEnum.movie_comment_page_hash_keys.value, douban_movie_id)))

    def parse(self, response):
        douban_movie_id = re.findall('subject/(\\d+)/comments', response.url)[0]
        movie_id = self.rdc.hget(RedisKeyEnum.movie_id_hash_keys.value, douban_movie_id)
        if response.status == 403 or response.status == 404:
            self.rdc.hdel(RedisKeyEnum.movie_id_hash_keys.value, movie_id)
            self.rdc.hdel(RedisKeyEnum.movie_comment_page_hash_keys.value, douban_movie_id)
            self.rdc.sadd(RedisKeyEnum.over_comment_movie_id_set.value, douban_movie_id)
            print("{} is 403 or 404".format(response.url))
            return
        comments = response.xpath('.//div[@class="comment-item"]')
        if comments is None or len(comments) < 2:
            self.rdc.hdel(RedisKeyEnum.movie_id_hash_keys.value, movie_id)
            self.rdc.hdel(RedisKeyEnum.movie_comment_page_hash_keys.value, douban_movie_id)
            self.rdc.sadd(RedisKeyEnum.over_comment_movie_id_set.value, douban_movie_id)
            print("{} has no comments or comments has been crawled".format(response.url))
            return

        print(response.url)
        for comment in comments:
            item = EvaluationItem()
            item['douban_comment_id'] = comment.xpath('.//@data-cid').extract_first()
            item['user'] = comment.xpath('.//div[@class="avatar"]/a/@title').extract_first()
            item['support_count'] = comment.xpath('.//span[@class="votes"]/text()').extract_first()
            item['comment_time'] = comment.xpath(
                './/span[@class="comment-info"]/span[@class="comment-time "]/@title').extract_first()
            comment_content_tag = comment.xpath('.//span[@class="short"]/text()').extract_first()
            if comment_content_tag is None:
                continue
            item['comment_content'] = comment_content_tag.strip().replace('\n', '').replace(' ', '')
            star_tag = comment.xpath('.//span[@class="comment-info"]/span/@class').extract_first()
            star_tag = re.findall('allstar(\\d+) rating', star_tag)
            if star_tag is None or len(star_tag) < 1:
                item['star'] = -1
            else:
                item['star'] = int(star_tag[0]) / 10
            item['already_watched'] = 1
            item['movie_id'] = movie_id
            yield item
        current_url = response.url
        if re.match('.*comments$', 'https://movie.douban.com/subject/30219700/comments'):
            page_no = 20
            current_url = self.url.format(douban_movie_id, page_no)
        else:
            page_no = int(re.findall('start=(\\d+)&limit=', current_url)[0]) + 20
            current_url = '{}{}&limit=20&sort=new_score&status=P'.format(current_url[:current_url.index('start=') + 6],
                                                                         str(page_no))
        self.rdc.hset(RedisKeyEnum.movie_comment_page_hash_keys.value, douban_movie_id, page_no)
        yield scrapy.Request(url=current_url, callback=self.parse)
        pass
