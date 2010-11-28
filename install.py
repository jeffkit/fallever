#!/usr/bin/env python
#coding=utf-8
from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.management import call_command
from settings import *
from blog.models import *
from django.contrib.auth.models import Group, Permission


def test_install():
    try:
        version = Version.objects.get(version=VERSION,in_use=True)
    except Exception,e:
        return e

def syncdb():
    call_command('syncdb',interactive=False)

def create_version(site_name):
    version = Version(version=VERSION,pre_version='None',site_name=site_name,app_type=APP_TYPE,in_use=True)
    version.save()

def create_perms():
    g = Group(name='blogger')
    g.save()
    g.permissions.add(
        Permission.objects.get(codename='add_blog'),
        Permission.objects.get(codename='change_blog'),
        Permission.objects.get(codename='delete_blog'),
        
        Permission.objects.get(codename='add_author'),
        Permission.objects.get(codename='change_author'),
        Permission.objects.get(codename='delete_author'),
        
        Permission.objects.get(codename='add_catelog'),
        Permission.objects.get(codename='change_catelog'),
        Permission.objects.get(codename='delete_catelog'),
        
        Permission.objects.get(codename='add_entry'),
        Permission.objects.get(codename='change_entry'),
        Permission.objects.get(codename='delete_entry'),
        
        Permission.objects.get(codename='change_comment'),
        Permission.objects.get(codename='delete_comment'),
        
        Permission.objects.get(codename='add_tag'),
        Permission.objects.get(codename='change_tag'),
        Permission.objects.get(codename='delete_tag'),
        
        Permission.objects.get(codename='add_link'),
        Permission.objects.get(codename='change_link'),
        Permission.objects.get(codename='delete_link'),
        
        Permission.objects.get(codename='add_panelinstance'),
        Permission.objects.get(codename='change_panelinstance'),
        Permission.objects.get(codename='delete_panelinstance'),
    )

    
def create_data():
    #内置Panel--------------------------------------------------------------------
    #Meta
    meta_template = u"""
    <ul>
	<li><a href="/admin/">登录</a></li>
	<li><a href="/admin/">管理博客</a></li>
	<li><a href="/feeds/blog/{{blog.shortcut}}/rss.xml">订阅文章&nbsp;<img height="12" src="/resource/img/feeds.png"/></a></li>
    </ul>
    """
    meta_panel = Panel(name=u'Meta',status=1,template=meta_template,method='fallever.blog.views.panels:meta')
    meta_panel.save()
    
    #评论面板
    comment_template = u"""
    <ul>
	{% for comment in comments %}
	<li><a href="/blog/{{blog.shortcut}}/{{comment.comment_to.id}}/#{{comment.id}}">
	
	{{comment.title}}
	
	({{comment.author_name}})</a></li>
	{% endfor%}
    </ul> 
    """
    comment_panel = Panel(name=u'最新评论',status=1,template=comment_template,method='fallever.blog.views.panels:comments')
    comment_panel.save()
    
    # 标签
    tag_template = u"""
    {% for tag in labels %}
	<a href="/blog/{{blog.shortcut}}/tag/{{tag.id}}/" class="tag_{{tag.level}}">{{tag.name}}</a>
    {% endfor%}
    """
    tag_panel = Panel(name=u'标签',status=1,template=tag_template,method='fallever.blog.views.panels:labels')   
    tag_panel.save()
    
    #日志分类面板
    catelog_template = u"""
    <ul>
	{% for cate in catelogs %}
	<li><a href="/blog/{{blog.shortcut}}/catelog/{{cate.id}}/">
	{% ifequal cate.name 'DEFAULT_CATELOG' %}
	未分类
	{% else %}
	{{cate.name}}
	{% endifequal%}
	
	({{cate.entryCount}})</a></li>
	{% endfor%}
    </ul>
    """
    catelog_panel = Panel(name=u'日志分类',status=1,template=catelog_template,method='fallever.blog.views.panels:catelogs')
    catelog_panel.save()
    
    
    #友情链接
    link_template = u"""
    <ul>
	{% for link in links %}
	<li><a href="{{link.link}}" target="_blank">{{link.caption}}</a></li>
	{% endfor%}
    </ul>
    """ 
    link_panel = Panel(name=u'友情链接',status=1,template=link_template,method='fallever.blog.views.panels:links')
    link_panel.save()
    
    #html
    html_template = u'{{html|safe}}'
    html_panel = Panel(name=u'HTML片段',status=0,template=html_template,method='fallever.blog.views.panels:html')
    html_panel.save()
    
    archive_template = u"""
    <ul class="entry-archive">
    {% for year_set in archive %}
        <li><a href="/blog/{{blog.shortcut}}/archive/{{year_set|first|first}}/" class="">{{year_set|first|first}}年  ({{year_set|first|last}})</a>
            {%ifequal forloop.counter 1%}
            <ul>
            {%else%}
            <ul style="display:none">
            {%endifequal%}
            {% for year_entry in year_set|last%}
                <li><a href="/blog/{{blog.shortcut}}/archive/{{year_set|first|first}}/{{year_entry|first}}/">{{year_entry|first}}月({{year_entry|last|length}})</a>
           {%ifequal forloop.counter 1%}
            <ul>
            {%else%}
            <ul style="display:none">
            {%endifequal%}
               {% for entry in year_entry|last%}
                   <li><a href="/blog/{{blog.shortcut}}/{{entry|first}}/">{{entry|last}}</a></li>
               {% endfor %}
           </ul>
            </li>
        {% endfor%}
    </ul>
    </li>
    {% endfor %}
    </ul>
    """
    archive_panel = Panel(name=u'归档',status=1,template=archive_template,method='fallever.blog.views.panels:archive')
    archive_panel.save()
    
    
if __name__ == '__main__':
    from blog.models import *
    for blog in Blog.objects.all():
        for entry in Entry.objects.filter(blog=blog):
            tag_str = [t.name for t in entry.tag_set.all()]
            
            ts = ' '.join(tag_str)
            entry.tag_str = ts
            entry.save()

    
