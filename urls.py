#!/usr/bin/env python
from django.conf.urls.defaults import *
from fallever.blog.views.rss import feeds
from fallever import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^grappelli/', include('grappelli.urls')),

    (r'^$','fallever.blog.views.index'),
    (r'^install/','fallever.blog.views.install.index'),
    (r'^feeds/(?P<url>.*)/rss.xml$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    
    (r'^blog/(?P<shortcut>\w+)/$', 'fallever.blog.views.blog_index'),
    (r'^blog/(?P<shortcut>\w+)/catelog/(?P<id>\d+)/$','fallever.blog.views.list_by_catelog'),
    (r'^blog/(?P<shortcut>\w+)/tag/(?P<id>\d+)/$','fallever.blog.views.list_by_tag'),
    (r'^blog/(?P<shortcut>\w+)/(?P<id>\d+)/$', 'fallever.blog.views.view_topic'),
    (r'^entry/(?P<id>\d+)/$', 'fallever.blog.views.view_entry'),
    
    (r'^blog/(?P<shortcut>\w+)/archive/(?P<year>\d{4})/$', 'fallever.blog.views.archive_year'),
    (r'^blog/(?P<shortcut>\w+)/archive/(?P<year>\d{4})/(?P<month>\d+)/$', 'fallever.blog.views.archive_month'),
    
    (r'^post_comment/(?P<id>\d+)/$','fallever.blog.views.comment'),
    (r'^delete_comment/(?P<entryID>\d+)/(?P<commentID>\d+)/$','fallever.blog.views.delete_comment'), 
    (r'^validate_code','fallever.blog.views.validateCode'),
     
     # for developer enviroment only
    (r'^resource/(?P<path>.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
