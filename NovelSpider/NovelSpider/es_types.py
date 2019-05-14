# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean,\
    analyzer, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["127.0.0.1"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class NovelType(DocType):
    suggest =Completion(analyzer=ik_analyzer)
    name = Text(analyzer="ik_max_word")
    author = Text(analyzer="ik_max_word")
    introduction = Text(analyzer="ik_max_word")
    url = Keyword()

    class Meta:
        index = "novel_search"
        doc_type = "novels"

    class Index:
        name = "novel_search"
        doc_type = "novels"


# 往es存数据之前需要先跑一下这个，执行初始化
if __name__ == "__main__":
    NovelType.init()
