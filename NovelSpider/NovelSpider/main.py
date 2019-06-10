import os

from scrapy.cmdline import execute

os.chdir(os.path.dirname(__file__))
execute(["scrapy", "crawl", "qidian"])