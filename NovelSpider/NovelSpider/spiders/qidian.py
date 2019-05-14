# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from NovelSpider.items import NovelspiderItem
import time

class QidianSpider(scrapy.Spider):
    name = 'qidian'
    allowed_domains = ['www.qidian.com',
                       'book.qidian.com']
    start_urls = ['https://www.qidian.com/all']

    def parse(self, response):
        item_nodes = response.css(".all-book-list .book-img-text .all-img-list li")
        for item_node in item_nodes:
            item_url = item_node.css(".book-mid-info h4 a::attr(href)").extract_first("")
            item_url = parse.urljoin(response.url, item_url)
            yield Request(url=item_url, callback=self.parse_detail)

        #获取下页url
        next_url = ""
        next_page = response.css(".page-box .pagination .lbf-pagination-item-list li")
        if len(next_page) == 0:
            # 请求返回的页面缺失，无法获取到下一页url，此时手动构造下页url
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            cur_url = response.url
            print(cur_url)
            tmps = cur_url.split("page=")
            if len(tmps) > 1:
                cur_page_num = int(tmps[1])
                next_page_num = cur_page_num + 1
                next_url = tmps[0] + "page=" + str(next_page_num)
            print(next_url)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        else:
            next_page = next_page[-1]
            next_url = next_page.css("li a::attr(href)").extract_first("")
        # time.sleep(1)
        print("next_url=" + next_url)
        if next_url:
            next_url = parse.urljoin(response.url, next_url)
            yield Request(url=next_url, callback=self.parse, errback=self.request_errback)

    def parse_detail(self, response):
        if response.status == 404:return
        url = response.url
        name = response.css(".book-information .book-info h1 em::text").extract_first("")
        author = response.css(".book-information .book-info h1 span a::text").extract_first("")
        # 类别标签
        labels = response.css(".book-information .book-info .tag a::text").extract()
        tags = ""
        for label in labels:
            if tags == "":tags = tags + label
            else: tags = tags + "," + label
        # 简介
        intros = response.css(".book-content-wrap .book-info-detail .book-intro p::text").extract()
        introduction = ""
        for intro in intros:
            introduction += intro.strip()

        item = NovelspiderItem()
        item["name"] = name
        item["author"] = author
        item["introduction"] = introduction
        item["tags"] = tags
        item["url"] = url
        item["source"] = "qidian"
        yield item

    def request_errback(self, failure):
        request = failure.request
        response = failure.value.response
        print(request.headers)
        # print(response.body)
        print(response.css("*"))


