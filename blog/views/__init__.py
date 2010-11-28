#!/usr/bin/env python
#coding=utf-8

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from fallever.blog.decorator import *
from fallever.blog.models import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from fallever.blog.utils.pagination import Pager
from django.http import Http404
import django.utils.simplejson as json
from fallever.blog.templatetags.dateFormat import nice
from django.template.defaultfilters import linebreaks
import random

#生成校验码
def validateCode(request):
    left = random.randint(0,10)
    right = random.randint(0,10)
    sum = left + right
    request.session['validate_total'] = str(sum)
    code = "%d&nbsp;+&nbsp;%d"%(left,right)
    return HttpResponse(code)

#验证校验码
def validate(request,total):
    if request.session['validate_total']:
        data = request.session['validate_total']
        del request.session['validate_total']
        if total == data:
            return True
    return False

#获得分页数
def get_page(request):
    if 'p' not in request.GET:
        page = Pager.page_def
    else:
        page = int(request.GET['p'])
    return page

#应用首页
def index(request):
    return HttpResponseRedirect('/blog/jeff/')

#某博客首页
@personal_blog_advise
def blog_index(request,shortcut,blog): 
    page = get_page(request)
    start = (page - 1) * Pager.maxlength_def
    count = blog.entry_set.filter(status=1).count()
    entries = blog.entry_set.filter(status=1).select_related(depth=1).order_by('-create_at')[start:start + Pager.maxlength_def]
    pager = Pager(None,count,page)
    return ('blog_index.html',{'entries':entries,'pager':pager,'url':'/blog/'+blog.shortcut + '/'})
    
#某博客分类文章列表
@personal_blog_advise
def list_by_catelog(request,shortcut,id,blog):
    page = get_page(request)
    start = (page - 1) * Pager.maxlength_def
    catelog = Catelog.objects.get(id=id)
    count = catelog.entry_set.filter(status=1).count()
    entries = catelog.entry_set.filter(status=1).select_related(depth=1).order_by('-create_at')[start:start + Pager.maxlength_def]
    pager = Pager(None,count,page)
    return ('blog_index.html',{'entries':entries,'catelog':catelog,'pager':pager,'url':'/blog/'+blog.shortcut + '/catelog/' + id + '/'})

#某博客标签文章列表
@personal_blog_advise
def list_by_tag(request,shortcut,id,blog):
    page = get_page(request)
    start = (page - 1) * Pager.maxlength_def
    tag = Tag.objects.get(id=id)
    count = tag.entrys.filter(status=1).count()
    entries = tag.entrys.filter(status=1).select_related(depth=1).order_by('-create_at')[start:start + Pager.maxlength_def]
    pager = Pager(None,count,page)
    return ('blog_index.html',{'entries':entries,'tag':tag,'pager':pager,'url':'/blog/'+blog.shortcut + '/tag/' + id + '/'})

#查看文章/blog/id/
@personal_blog_advise
def view_topic(request,shortcut,id,blog):
    ''' view detail of topic.also load comments.'''
    try:
        entry = Entry.objects.select_related(depth=1).get(id=id,blog=blog)
        if entry.status == 0:
            raise ObjectDoesNotExist
        comments_of_entry = entry.comment_set.filter(status=1).order_by('id')# all comments
    except ObjectDoesNotExist:
        raise Http404
    return ('view_topic.html',{'entry':entry,'comments_of_entry':comments_of_entry})

#查看文章/entry/id/来自Feeds
def view_entry(request,id):
    try:
        entry = Entry.objects.get(id=id)
        if entry.status == 0:
            raise ObjectDoesNotExist
        comments_of_entry = entry.comment_set.filter(status=1).order_by('id')# all comments
    except ObjectDoesNotExist:
            raise Http404
    blog = entry.blog
    datas = get_common_data_by_blog(blog,request)
    #panels = blog.panelinstance_set.order_by('column').order_by('row')
    datas['entry'] = entry
    datas['comments_of_entry'] = comments_of_entry
    #datas['panels'] = panels
    return render_to_response('view_topic.html',context_instance=RequestContext(request, datas))
    

#评论
def comment(request,id):
    p = request.POST
    #step1,校验
    code = p['validate_code']
    if not validate(request,code):
        return HttpResponse("{result:'fail',message:'看起来您老的数学不像那么差的呀。。'}")
    if len(p['name']) == 0 or len(p['content']) == 0:
        return HttpResponse("{result:'fail',message:'您手真快！但好像忘了填名字或说几句了？'}")
    try:
        comment_to = Entry.objects.get(id = id)
    except ObjectDoesNotExist:
        return HttpResponse('评论无效')
    
    #step2，处理数据
    link = p['link']
    if link.strip() == '':
        link = None

    if len(p['title']) == 0 :
        title = 'RE:' + comment_to.title
    
    account = None
    if request.user.is_authenticated():
        account = request.user
    
    #step3，生成评论
    comment = Comment(title=p['title'],author_name=p['name'],content=p['content'],ip=request.META['REMOTE_ADDR'],
    comment_to=comment_to,blog=comment_to.blog,author=account,link=link)
    comment.save()
    
    #step4，返回结果
    result = {'result':'success'}
    dictionary = {'id':comment.id,
            'link':comment.link,
            'author':comment.author_name,
            'time':nice(comment.comment_time),
            'title':comment.title,
            'content':linebreaks(comment.content),
            'count':comment_to.comment_count}
    result['comment'] = dictionary
    
    return HttpResponse(json.dumps(result))

#删除评论
def delete_comment(request,entryID,commentID):
    comment = Comment.objects.get(id=commentID)
    comment.delete()
    entry = Entry.objects.get(id=entryID)
    entry.comment_count = entry.comment_count - 1
    entry.save()
    return HttpResponseRedirect('/entry/%s/' % entry.id)
    
@personal_blog_advise
def archive_year(request,shortcut,year,blog):
    page = get_page(request)
    start = (page - 1) * Pager.maxlength_def
    count = blog.entry_set.filter(status=1,create_at__year=year).count()
    entries = blog.entry_set.filter(status=1,create_at__year=year).order_by('-create_at')[start:start + Pager.maxlength_def]
    pager = Pager(None,count,page)
    return ('blog_index.html',{'entries':entries,'pager':pager,'url':'/blog/'+blog.shortcut + '/archive/' + str(year) + '/'})
    
@personal_blog_advise
def archive_month(request,shortcut,year,month,blog):
    page = get_page(request)
    start = (page - 1) * Pager.maxlength_def
    count = blog.entry_set.filter(status=1,create_at__year=year,create_at__month=month).count()
    entries = blog.entry_set.filter(status=1,create_at__year=year,create_at__month=month).order_by('-create_at')[start:start + Pager.maxlength_def]
    pager = Pager(None,count,page)
    return ('blog_index.html',{'entries':entries,'pager':pager,'url':'/blog/'+blog.shortcut + '/archive/' + str(year) + '/' + '/' + str(month) + '/'})
