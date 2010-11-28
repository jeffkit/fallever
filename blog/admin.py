#coding=utf-8

from django.contrib import admin
from fallever.blog import models
from django.shortcuts import render_to_response

def filter_blog(name,db_field,request,**kwargs):
    if db_field.name == name:
        kwargs["queryset"] = models.Blog.objects.filter(owner=request.user)
        return db_field.formfield(**kwargs)
    return None

def filter_catelog(name,db_field,request,**kwargs):
    if db_field.name == name:
        blogs = request.user.blog_set.all()
        kwargs["queryset"] = models.Catelog.objects.filter(blog__in = blogs)
        return db_field.formfield(**kwargs)
    return None

def create_blog(user,blog):
    # 新创建，为博客加上默认分类、默认面板，甚至一篇Hello world。
    def_cate = models.Catelog(blog=blog,name=u'默认分类',description=u'系统为用户添加的默认分类')
    def_cate.save()
    
    sample = u"""
        大家好，我的新博客在<a href="http://www.fallever.com">Fallever</a>安家了，新地址在<a href="http://www.fallever.com/blog/%s/">http://www.fallever.com/blog/%s/</a>,欢迎大家多点来踩来看我。祝大家生活愉快！
    """%(blog.shortcut,blog.shortcut)
    hello = models.Entry(title=u"我的博客在Fallever安家了，欢迎光临！",catelog=def_cate,author=user,blog=blog,content=sample)
    hello.save()
    
    panels = models.Panel.objects.filter(status=1)
    for i in range(len(panels)):
        panels[i].create_instance(blog,0,i)
    

class BlogAdmin(admin.ModelAdmin):
    list_display = ['caption','shortcut','sub_caption','owner']
    list_filter = ['create_at']
    search_fields = ['caption','sub_caption']
    ordering = ['-create_at']
    
    fieldsets = ((None,{'fields':('caption','sub_caption','shortcut')}),)

    def queryset(self, request):
        qs = super(BlogAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'owner', None) is None:
            obj.owner = request.user
        obj.save()
        if not change:
            create_blog(request.user,obj)



admin.site.register(models.Blog,BlogAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','description','entryCount','blog']
    search_fields = ['name','description']
    ordering = ['blog']
    radio_fields = {'blog':admin.VERTICAL}
    
    def queryset(self, request):
        qs = super(CategoryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        #找到当前用户对应的博客
        blogs = request.user.blog_set.all()
        return qs.filter(blog__in = blogs)
    
    #外键只显示与用户相关的选项。
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return filter_blog('blog',db_field,request,**kwargs) or super(CategoryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.Catelog,CategoryAdmin)

class EntryAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/tiny_mce/tiny_mce.js','js/admin/entry_add.js')
        #js = ('admin/tinymce/jscripts/tiny_mce/tiny_mce.js','filebrowser/js/TinyMCEAdmin.js')

    list_display = ['title','catelog','status','create_at','tag_str']
    search_fields = ['title','content']
    ordering = ['-create_at']
    list_filter = ['create_at']
    actions = ['apply_tags']
    
    fieldsets = (
        (None, {
            'fields': ('title','catelog','content','tag_str')
        }),
        ('高级选项', {
            'fields': ('status', 'comment_enable')
        }),
    )
    
    def apply_tags(self,request,queryset):
        print 'hello'
        return render_to_response('admin/entry/apply_tags.html',{'entries':queryset})
    apply_tags.short_description = u'添加标签'
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.last_update_by = request.user.username
        obj.ip = request.META['REMOTE_ADDR']
        obj.blog = obj.catelog.blog
        obj.save()
    def queryset(self, request):
        qs = super(EntryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return filter_catelog('catelog',db_field,request,**kwargs) or super(EntryAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.Entry,EntryAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['content','title','author_name','comment_time','ip','status']
    list_filter = ['comment_time']
    search_fields = ['title','content','author_name']
    fieldsets = (
        (None, {
            'fields': ('comment_to','title','author_name','link','content')
        }),
        ('高级选项', {
            'fields': ('status','ip')
        }),
    )
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.author_name = request.user.username
        obj.last_update_by = request.user.username
        obj.ip = request.META['REMOTE_ADDR']
        obj.blog = obj.comment_to.blog
        obj.save()

    def queryset(self, request):
        qs = super(CommentAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        #找到当前用户对应的博客
        blogs = request.user.blog_set.all()
        return qs.filter(blog__in = blogs)
    

admin.site.register(models.Comment,CommentAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ['name','entryCount']
    search_fields = ['name']
    filter_horizontal = ['entrys']
    ordering = ['blog']
    
    def queryset(self, request):
        qs = super(TagAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        #找到当前用户对应的博客
        blogs = request.user.blog_set.all()
        return qs.filter(blog__in = blogs)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return filter_blog('blog',db_field,request,**kwargs) or super(TagAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.Tag,TagAdmin)

class LinkAdmin(admin.ModelAdmin):
    list_display = ['link','caption','blog']
    #list_filter = ['blog']
    search_fields = ['caption','link']
    fieldsets = ((None,{'fields':('blog','caption','link')}),)
    list_editable = ['caption']
    ordering = ['blog']
    
    def queryset(self, request):
        qs = super(LinkAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        #找到当前用户对应的博客
        blogs = request.user.blog_set.all()
        return qs.filter(blog__in = blogs)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return filter_blog('blog',db_field,request,**kwargs) or super(LinkAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.Link,LinkAdmin)

class PanelAdmin(admin.ModelAdmin):
    list_display = ['name','method','status']
    list_filter = ['status']
    search_fields = ['name']
# 只允许超级管理员访问
admin.site.register(models.Panel,PanelAdmin)

class PanelInstanceAdmin(admin.ModelAdmin):
    list_display = ['title','panel','blog']
    list_filter = ['panel','column']
    search_fields = ['title']
    ordering = ['blog']
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return filter_blog('blog',db_field,request,**kwargs) or super(PanelInstanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    def queryset(self,request):
        qs = super(PanelInstanceAdmin,self).queryset(request)
        if request.user.is_superuser:
            return qs
        blogs = request.user.blog_set.all()
        return qs.filter(blog__in = blogs)
admin.site.register(models.Panelinstance,PanelInstanceAdmin)
