#!/usr/bin/env python
#coding=utf-8
from django.core.management import call_command
from fallever.settings import *
from fallever.blog.models import *
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from fallever.install import *
from django.db import transaction
from fallever.blog.forms import *
from django.shortcuts import render_to_response
from django.contrib.auth.models import User

#创建数据库（使用manage.py的方法创建数据库，数据库的配置只能手动修改配置文件）
#初始化数据（管理员数据、权限分组、内置面板等）
#@transaction.commit_manually
def index(request):
    #检测是否已安装过，如果没有则检测数据库的配置是否可用，可用则创建数据库。
    if request.method == 'POST':
        return handle_form(request)
    sth_wrong = test_install()
    print sth_wrong
    if sth_wrong:
        try:
            #尝试一下同步数据库
            syncdb()
            form = SetupForm()
            return render_to_response('install_form.html',{'form':form})
            return HttpResponse(u'已创建数据表了')
        except:
            #transaction.rollback()#对mysql没用的
            return HttpResponse(u'访问数据库的时候出了些问题，请检查settings.py的数据库配置信息是否可用并正确。如果用Mysql数据库，请使用UTF-8编码。')
            # 返回一个让用户输入站点标题及管理员帐号的页面。TODO
        return HttpResponse(u'安装过程中遇到了一些未知的问题，请联系<a href="mailto:jeff@fallever.com">jeff@fallever.com</a>解决。')
    else:
        HttpResponseRedirect('/') #已经安装了，回首页！
    

def handle_form(request):
    #保存网站名字，管理员帐号。初始化数据。
    form = SetupForm(request.POST)
    if form.is_valid():
        site_name = form.cleaned_data['site_name']
        admin_name = form.cleaned_data['admin_name']
        admin_psw = form.cleaned_data['admin_psw']
        admin_email = form.cleaned_data['admin_mail']
        
        User.objects.create_superuser(admin_name,admin_email,admin_psw)
        
        create_perms()
        create_data()
        create_version(site_name)
    else:
        return render_to_response('install_form.html',{'form':form})
    
    # 返回安装成功页面
    return HttpResponse(u'恭喜你，安装成功了！马上返回首页使用吧！')
