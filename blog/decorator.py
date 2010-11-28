#!/usr/bin/env python
#coding=utf-8

from django.http import HttpResponse
from fallever.blog.models import Blog
from fallever.blog.models import Comment
#from fallever.blog.views import SESSION_USER_ID_KEY
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.exceptions import ObjectDoesNotExist
def display_login_form(request,error):
    return render_to_response('login.html',{'error':error})

#check login
def need_login(func):
    ''' check if current session.does the user login?  '''
    def check_login(request,*args,**kwargs):
        assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        if request.user.is_authenticated:
            return func(request,*args,**kwargs)
        return display_login_form(request,'您必须先登录')
    return check_login

#博客管理
def blog_manage_layout(func):
    def manage(request,shortcut,*args,**kwargs):
        try:
            blog = Blog.objects.select_related(depth=1).get(shortcut=shortcut)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/')
        kwargs['blog'] = blog
        result = func(request,shortcut,*args,**kwargs)
        if type(result) != tuple:
            return result
        template_name = result[0]
        data = result[1]
        
        if request.user.is_authenticated and blog.owner.id == request.user.id:
            return render_to_response(template_name,data,context_instance=RequestContext(request, {'blog':blog}))
        else:
            return HttpResponse('只有博客管理员才能对此博客进行管理')
    return manage

    

def personal_blog_advise(func):
    '''个人博客的装饰器，获得中心内容以外的常用块如分类、连接等。使得View方法出需要关心业务数据'''
    def view(request,shortcut,*args,**kwargs):   
        try:
            blog = Blog.objects.select_related(depth=1).get(shortcut=shortcut)
        except ObjectDoesNotExist:
            return HttpResponse("找不到你请求的资源")
        common = get_common_data_by_blog(blog,request,*args,**kwargs)  
        kwargs['blog'] = blog
        result = func(request,shortcut,*args,**kwargs)
        if type(result) != tuple:
            return result
        template_name = result[0]
        data = result[1]
            
        return render_to_response(template_name,data,context_instance=RequestContext(request, common))
    return view

def get_common_data_by_blog(blog,request,*args,**kwargs):
    #获得该Blog的Panel
    panels = blog.panelinstance_set.filter(blog=blog).select_related(depth=1).order_by('column').order_by('row')
    catelogs = blog.catelog_set.all()
    return {'blog':blog,'panels':panels,'catelogs':catelogs}

def login_info(request):
    def check(request,*args,**kwargs):
        pass
    return check
