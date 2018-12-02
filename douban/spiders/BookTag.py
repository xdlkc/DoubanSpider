# -*- coding: utf-8 -*-
import scrapy


class BooktagSpider(scrapy.Spider):
    name = 'BookTag'
    allowed_domains = []
    start_urls = ['https://book.douban.com/tag/?view=type']

    def parse(self, response):
        print(response.xpath('//tr'))

        pass
