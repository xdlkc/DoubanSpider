# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EvaluationItem(scrapy.Item):
    """
    影评item
    """
    user = scrapy.Field()
    already_watched = scrapy.Field()
    star = scrapy.Field()
    douban_comment_id = scrapy.Field()
    comment_content = scrapy.Field()
    comment_time = scrapy.Field()
    support_count = scrapy.Field()
    movie_id = scrapy.Field()


class MovieItem(scrapy.Item):
    """
    电影item
    """
    score = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    cover_url = scrapy.Field()
    douban_movie_id = scrapy.Field()


class MovieAndTypeItem(scrapy.Item):
    movie_id = scrapy.Field()
    movie_type_id = scrapy.Field()
