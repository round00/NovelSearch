# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from NovelSpider.items import NovelspiderItem
import time

class ZonghengSpider(scrapy.Spider):
    name = 'zongheng'
    allowed_domains = ['book.zongheng.com']
    start_urls = ['http://book.zongheng.com/store.html']

    def parse(self, response):
        item_nodes = response.css(".store_list_wrap .store_collist .bookbox fl")
        for item_node in item_nodes:
            item_url = item_node.css(".bookinfo .bookname a::attr(href)").extract_first("")
            item_url = parse.urljoin(response.url, item_url)
            yield Request(url=item_url, callback=self.parse_detail)

        item_nodes = response.css(".store_list_wrap .store_collist .bookbox fr")
        for item_node in item_nodes:
            item_url = item_node.css(".bookinfo .bookname a::attr(href)").extract_first("")
            item_url = parse.urljoin(response.url, item_url)
            yield Request(url=item_url, callback=self.parse_detail)

        #获取下页url
        next_url = ""
        next_page = response.css(".pagebox .pagenumber.pagebar a[title]::attr(page)")
        if len(next_page) != 0:
            next_url = 'http://book.zongheng.com/store/c0/c0/b0/u0/p'+next_page+'/v9/s9/t0/u0/i1/ALL.html'
        # time.sleep(1)
        print("next_url=" + next_url)
        if next_url:
            yield Request(url=next_url, callback=self.parse, errback=self.request_errback)

    def parse_detail(self, response):
        if response.status == 404:return
        url = response.url
        name = response.css(".book-detail.clearfix .book-info .book-name::text").extract_first("")
        author = response.css(".book-top.clearfix .book-side.fr .book-author.eye-pretector-precessed .au-head em::text").extract_first("")
        # 类别标签
        labels = response.css(".book-detail.clearfix .book-info .book-label span a::text").extract()
        tags = ""
        for label in labels:
            if tags == "":tags = tags + label
            else: tags = tags + "," + label
        # 简介
        intros = response.css(".book-detail.clearfix .book-info .book-dec.Jbook-dec.hide p::text").extract()
        introduction = ""
        for intro in intros:
            introduction += intro.strip()

        item = NovelspiderItem()
        item["name"] = name
        item["author"] = author
        item["introduction"] = introduction
        item["tags"] = tags
        item["url"] = url
        item["source"] = "zongheng"
        yield item

    def request_errback(self, failure):
        request = failure.request
        response = failure.value.response
        print(request.headers)
        # print(response.body)
        print(response.css("*"))


