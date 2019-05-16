# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from NovelSpider.items import NovelspiderItem
import time


class XiaoxiangSpider(scrapy.Spider):
    name = 'xiaoxiang'
    allowed_domains = ['www.xxsy.net']
    start_urls = ['http://www.xxsy.net/search']

    def parse(self, response):
        item_nodes = response.css(".result-list li")
        for item_node in item_nodes:
            item_url = item_node.css(".info h4 a::attr(href)").extract_first("")
            item_url = "www.xxsy.net" + item_url
            yield Request(url=item_url, callback=self.parse_detail)

        # 获取下页url
        next_url = ""
        next_page = response.css(".pages .page-next::attr(onclick)").extract_first("")
        if len(next_page) != 0:
            next_page = next_page[8:-1]
            next_url = 'http://www.xxsy.net/search?s_wd=&sort=9&pn=' + next_page
        # time.sleep(1)
        print("next_url=" + next_url)
        if next_url:
            yield Request(url=next_url, callback=self.parse, errback=self.request_errback)

    def parse_detail(self, response):
        if response.status == 404: return
        url = response.url
        name = response.css(".bookdetail .bookprofile .title h1::text").extract_first("")
        author = response.css(".bookdetail .bookprofile .title span a::text").extract_first("")
        # 类别标签
        labels = response.css(".bookdetail .bookprofile .sub-cols span:nth-last-child(2)::text").extract_first("")
        tags = labels[3:]
        # 简介
        ps = response.css(".box-con .click-bd .book-profile .introcontent dd p::text").extract()
        introduction = ""
        for p in ps:
            introduction += p
        item = NovelspiderItem()
        item["name"] = name
        item["author"] = author
        item["introduction"] = introduction
        item["tags"] = tags
        item["url"] = url
        item["source"] = "xiaoxiang"
        yield item

    def request_errback(self, failure):
        request = failure.request
        response = failure.value.response
        print(request.headers)
        # print(response.body)
        print(response.css("*"))
