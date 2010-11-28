#!/usr/bin/env python
#coding=utf-8
from django import template
def page_info(pager, url):
    return {'pager':pager,'url':url}

register = template.Library()
register.inclusion_tag('common/pagination.html')(page_info)
