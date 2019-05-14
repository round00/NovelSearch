# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import redis
from NovelSpider.es_types import NovelType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(hosts=["localhost"])
redis_cli = redis.StrictRedis()


def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, params={}, body={'text' : text, 'analyzer':"ik_max_word", 'filter':["lowercase"]})
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})

    return suggests


class NovelspiderItem(scrapy.Item):
    name = scrapy.Field()
    author = scrapy.Field()
    introduction = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()

    def save_to_es(self):
        novel = NovelType()
        novel.name = self['name']
        novel.author = self['author']
        novel.introduction = self['introduction']
        novel.tags = self["tags"]
        novel.url = self["url"]
        novel.source = self["source"]
        novel.suggest = gen_suggests(NovelType.Index.name, ((novel.name, 10), (novel.introduction, 7), (novel.author, 7)))
        redis_cli.incr(self["source"] + "_count")
        novel.save()

