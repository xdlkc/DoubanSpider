# -*- coding: utf-8 -*-

import logging

from douban.enums import *
from douban.items import *
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from douban.utils import MysqlManager, format_date, RedisManager


class DoubanPipeline(object):
    def __init__(self):
        self.db_manager = MysqlManager()
        self.rm = RedisManager()

    def process_item(self, item, spider):
        try:
            if isinstance(item, EvaluationItem):
                self.process_evaluation_item(item)
            elif isinstance(item, MovieItem):
                self.process_movie_item(item, spider)
            elif isinstance(item, MovieAndTypeItem):
                pass
        except Exception as e:
            msg = "crawl err,item:{}, e:{}".format(item, e)
            print(msg)
            logging.error(msg)
            # 抓取出现异常，发送停止信号
            spider.crawler.engine.close_spider(spider, 'process_movie_item err:{}'.format(e))

    def process_evaluation_item(self, item):
        """
        处理影评item
        :param item:
        :return:
        """
        douban_comment_id = item['douban_comment_id']

        movie_id = item['movie_id']
        if self.rm.rdc.sismember(RedisKeyEnum.over_movie_comment_set.value, douban_comment_id):
            logging.log(logging.WARNING,
                        "process_evaluation_item {}:{} has already crawled".format(douban_comment_id, movie_id))
            return
        comment_time = format_date(item['comment_time'])
        ins_sql = 'insert into movie_evaluation (movie_id,user, already_watched, star, douban_comment_id, ' \
                  'comment_content, comment_time,support_count) values (%s,%s,%s,%s,%s,%s,%s,%s);'
        self.db_manager.execute_dml(ins_sql, movie_id, item['user'], item['already_watched'], item['star'],
                                    item['douban_comment_id'], item['comment_content'], comment_time,
                                    item['support_count'])
        self.rm.rdc.sadd(RedisKeyEnum.over_movie_comment_set.value, douban_comment_id)

    def process_movie_item(self, item, spider):
        """
        处理影片item
        :param item:
        :param spider:
        :return:
        """
        ins_sql = 'insert into movie (score, title, url, directors, actors, cover_url, douban_movie_id) ' \
                  'values (%s,%s,%s,%s,%s,%s,%s);'
        douban_movie_id = item['douban_movie_id']
        title = item['title']
        if self.rm.rdc.hget(RedisKeyEnum.over_movie_id_hash_keys.value, douban_movie_id):
            logging.log(logging.WARNING, "process_movie_item {}:{} has already crawled".format(douban_movie_id, title))
            return
        self.db_manager.execute_dml(ins_sql, item['score'], title, item['url'], item['directors'], item['actors'],
                                    item['cover_url'], item['douban_movie_id'])
        self.rm.rdc.hset(RedisKeyEnum.over_movie_id_hash_keys.value, douban_movie_id, 1)
