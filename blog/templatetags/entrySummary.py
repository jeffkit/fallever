#!/usr/bin/env python
#coding=utf-8
from django import template
def entry_summary(entry,user):
    return {'entry':entry,'user':user,'tags':entry.tag_set.all()}

register = template.Library()
register.inclusion_tag('common/entrySummary.html')(entry_summary)
