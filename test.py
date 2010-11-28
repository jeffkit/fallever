#!/usr/bin/env python
#coding=utf-8
from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import call_command
from settings import *
from blog.models import *
import feedparser
from datetime import datetime

def import_blogspot(url,blog):
    feeds = feedparser.parse(url)
    cate = Catelog.objects.get(id=5)
    for entry in feeds.entries:
        dt = datetime(*entry.date_parsed[:6])
        title = entry.title
        desc = entry.summary
        en = Entry(title=title,content=desc,catelog=cate,blog=blog,author=blog.owner,create_at=dt)
        en.save()

if __name__ == '__main__':
    blog = Blog.objects.get(id=1)
    import_blogspot('http://jeff-jie.blogspot.com/feeds/posts/default?alt=rss',blog)
