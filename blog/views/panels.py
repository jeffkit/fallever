#!/usr/bin/env python
#coding=utf-8
from fallever.blog.models import Comment
from django import template

def comments(request,panel,blog):
    comments = Comment.objects.select_related(depth=1).filter(blog=blog).order_by('-comment_time')[:10]
    return template.Context({'comments':comments,'blog':blog})

def labels(request,panel,blog):
    labels = blog.tag_set.all()
    return template.Context({'labels':labels,'blog':blog})

def catelogs(request,panel,blog):
    catelogs = blog.catelog_set.all()
    return template.Context({'catelogs':catelogs,'blog':blog})

def links(request,panel,blog):
    links = blog.link_set.all()
    return template.Context({'links':links})

def html(request,panel,blog):
    return template.Context({'html':panel.parameters})
    
def meta(request,panel,blog):
    return template.Context({'blog':blog})

def archive(request,palen,blog):
    def get_year_total(year_entry_set):
        total = 0
        for ys in year_entry_set:
            total += len(ys[1])
        return total
    """
    返回的结果集格式如下：
    [[[2009,30],[[12,[{'3':'文章一'},{'4':'文章二'}]],
           [11,[{'1':'文章一'},{'2':'文章二'}]]],       
           ......
    ],
    [2008 ...],
    [2007 ...],
    ......
    ]
    """
    result = []
    year_set = []
    year_entry_set = []
    month_set = []
    month_entry_set = []
    current_year = 0
    current_month = -1
    
    #year_url_tpl = '/blog/%s/archive/%s/'
    #month_url_tpl = '/blog/%s/archive/%s-%s/'
    #entry_url_tpl = '/blog/%s/%s/'
    
    entries = blog.entry_set.filter(status=1).values('id','title','create_at').order_by('-create_at')
    
    # 每个Entry判断年及月，将其加入合适的列表中即可。
    for entry in entries:
        if not entry['create_at']:continue
        create_at = entry['create_at']
        year = create_at.year
        if year != current_year: 
            #如果出现新的年份，将上一个年份的列表添加到结果集，再创建新的年份列表。
            if year_set:
                year_set[0].append(get_year_total(year_entry_set))
            year_entry_set = []
            year_set = [[create_at.year],year_entry_set]
            result.append(year_set)
            current_year = year
        
        month = create_at.month
        if month != current_month:
            #如果出现新的月份，将上一月份的列表添加到年份列表，再创建新的月份列表及文章列表
            month_entry_set = []
            month_set = [create_at.month,month_entry_set]
            year_entry_set.append(month_set)
            current_month = month
        month_entry_set.append((entry['id'],entry['title']))
    year_set[0].append(get_year_total(year_entry_set))
    return template.Context({'archive':result,'blog':blog})
