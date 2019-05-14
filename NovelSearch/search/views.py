import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import NovelType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()


def bytes_2_int(bytes):
    if bytes is None:return 0
    return int(bytes)


def bytes_2_str(bytes):
    if bytes is None:return ""
    return str(bytes, encoding="utf8")


def get_topnsearch():
    keywords = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
    topn_search = []
    for key in keywords:
        topn_search.append(bytes_2_str(key))
    return topn_search


def get_source_name(source):
    if source is None:return ""
    if source == "qidian":return "起点中文网"
    elif source == "zongheng": return "纵横中文网"
    elif source == "jinjiang": return "晋江文学城"
    else: return "其他"


class IndexView(View):
    #首页
    def get(self, request):
        topn_search = get_topnsearch()
        return render(request, "index.html", {"topn_search":topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s = NovelType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field":"suggest", "fuzzy":{
                    "fuzziness":2
                },
                "size": 10
            })
            suggestions = s.execute()
            for match in suggestions.suggest.my_suggest[0].options:
                source = match._source
                re_datas.append(source["name"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


class SearchView(View):
    def get(self, request):
        #获取搜索关键字
        key_words = request.GET.get("q", "")
        #获取当前选择搜索的范围
        # s_type = request.GET.get("s_type", "novel")

        redis_cli.zincrby("search_keywords_set", 1 ,key_words)

        topn_search = get_topnsearch()
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1
        #从redis查看该类数据总量
        qidian_count = bytes_2_int(redis_cli.get("qidian_count"))
        jinjiang_count = bytes_2_int(redis_cli.get("jinjiang_count"))
        zongheng_count = bytes_2_int(redis_cli.get("zongheng_count"))

        start_time = datetime.now()
        #根据关键字查找
        response = client.search(
            index="novel_search",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["name", "author", "introduction"]
                    }
                },
                "from": (page - 1) * 10,
                "size": 10,
                #对关键字进行高光标红处理
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "name": {},
                        "introduction": {},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "highlight" in hit and "name" in hit["highlight"]:
                hit_dict["name"] = "".join(hit["highlight"]["name"])
            else:
                hit_dict["name"] = hit["_source"]["name"]
            if "highlight" in hit and "introduction" in hit["highlight"]:
                hit_dict["introduction"] = "".join(hit["highlight"]["introduction"])[:500]
            else:
                hit_dict["introduction"] = hit["_source"]["introduction"][:500]

            hit_dict["source"] = get_source_name(hit["_source"]["source"])
            hit_dict["tags"] = hit["_source"]["tags"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["author"] = hit["_source"]["author"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "qidian_count": qidian_count,
                                               "zongheng_count": zongheng_count,
                                               "jinjiang_count": jinjiang_count,
                                               "topn_search": topn_search})
