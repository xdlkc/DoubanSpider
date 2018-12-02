# -*- coding: utf-8 -*-
import scrapy


class BooktagSpider(scrapy.Spider):
    """
    豆瓣图书爬虫：未开始
    """
    name = 'book_tag'
    allowed_domains = []
    start_urls = ['https://book.douban.com/tag/?view=type']

    def parse(self, response):
        print(response.xpath('//tr'))

        pass
