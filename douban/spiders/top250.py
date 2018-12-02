# -*- coding: utf-8 -*-
import scrapy


class Top250Spider(scrapy.Spider):
    name = 'top250'
    allowed_domains = ['https://movie.douban.com/top250']
    start_urls = ['https://movie.douban.com/top250/']

    def parse(self, response):
        pass
