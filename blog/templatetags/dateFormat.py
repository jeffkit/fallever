#!/usr/bin/env python
#coding=utf-8
from datetime import datetime
from django import template

register = template.Library()

#以更人性化的方式显示时间，如两分钟前，一周前，一个月前等。
def nice(value):
    now = datetime.now()
    delta = now - value
    if delta.days:
        if delta.days < 30:
            return "%d天之前"%delta.days
        else:
            return value.strftime('%Y-%m-%d')
    elif delta.seconds:
        if delta.seconds < 60:
            return "不到1分钟之前"
        elif delta.seconds < 3600:
            return "%d分钟之前"%(delta.seconds/60)
        else:
            return "%d小时之前"%(delta.seconds/3600)
    else: 
        return "不到1分钟之前"
        
register.filter('nice',nice)