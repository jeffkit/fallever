#!/usr/bin/env python
#coding=utf-8
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from fallever.blog.models import *


class recent_blog_entry(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Blog.objects.get(shortcut=bits[0])

    def title(self,blog):
        return blog.caption

    def link(self,blog):
        return '/blog/%s/' % blog.shortcut

    def description(self,blog):
        return blog.sub_caption

    def items(self,blog):
        return Entry.objects.filter(blog=blog,status=1).order_by('-create_at')[:10]

    def item_pubdate(self,item):
        return item.create_at

    def item_link(self,item):
        return '/entry/%s/' % item.id

class export_blog_entry(recent_blog_entry):
    def items(self,blog):
        return Entry.objects.filter(blog=blog,status=1).order_by('-create_at')

feeds = {'blog':recent_blog_entry}
export_feeds =  {'blog':export_blog_entry}
