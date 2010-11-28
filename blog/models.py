#!/usr/bin/env python
#coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.core.exceptions import ObjectDoesNotExist

class Version(models.Model):
    APP_TYPE = (
        (0,u'单人版'),
        (1,u'多人版')
    )
    version = models.CharField(u'版本号',max_length=10)
    pre_version = models.CharField(u'从哪个版本号升级',max_length=10)
    install_at = models.DateTimeField(u'安装时间',auto_now_add=True)
    in_use = models.BooleanField(u'当前使用的版本')
    app_type = models.IntegerField(u'版本',default=1,choices=APP_TYPE)
    site_name = models.CharField(u'站点名',max_length=50)
    
    def __unicode__(self):
        return "%s-%d"%(self.version,self.app_type)
    
class Blog(models.Model):
    caption = models.CharField(u'名称',max_length=50,help_text=u'显示在您的博客页面的顶端')
    sub_caption = models.CharField(u'副标题',max_length=200,blank=True,help_text=u'为您的博客添加副标题，可以留白')
    owner = models.ForeignKey(User,verbose_name=u'用户',null=True,blank=True)# 创建人、超管
    create_at = models.DateTimeField(u'创建时间',auto_now_add=True)
    shortcut = models.CharField(u'个性地址',max_length=10,blank=True,null=True,unique=True,help_text=u'如果你填jeff，那么人们可以通过http://fallever.com/blog/jeff/来访问您的博客。')
    
    def __unicode__(self):
        return self.caption
        
    class Meta:
        verbose_name = u'博客'
        verbose_name_plural = u'博客'
#-------------------------------------------------------------------------------
# 作者与博客的关系，支持一博多作者。

class Author(models.Model):
    AUTHOR_ROLE = (
        (0,u'编辑'),
        (1,u'管理员')
    )

    blog = models.ForeignKey(Blog,verbose_name=u'博客')
    user = models.ForeignKey(User,verbose_name=u'用户')
    role = models.IntegerField(u'角色',choices=AUTHOR_ROLE)
    creator = models.CharField(u'创建人',max_length=100)
    join_at = models.DateTimeField(u'创建时间',auto_now=True)
    
    def __unicode__(self):
        return '%s on %s' % (self.user.username,self.blog.caption)
    
    class Meta:
        verbose_name = u'作者'
        verbose_name_plural = u'作者'
#-------------------------------------------------------------------------------
class Catelog(models.Model):
    blog = models.ForeignKey(Blog,verbose_name=u'所属博客',help_text=u'您正在创建的分类将要添加到哪个博客？')
    name = models.CharField(u'分类名',max_length=50)
    description = models.CharField(u'说明',max_length=100,null=True,blank=True)
    entryCount = models.IntegerField(u'文章数',default=0,editable=False)
    
    def __unicode__(self):
        return '%s - (%s)'%(self.name,self.blog.caption)
    
    class Meta:
        verbose_name = u'分类'
        verbose_name_plural = u'分类'
#-------------------------------------------------------------------------------
class Entry(models.Model):
    ENTRY_STATUS = (
        (1,u'公开'),
        (0,u'草稿')
    )
    title = models.CharField(u'标题',max_length=100)
    content = models.TextField(u'内容')
    author = models.ForeignKey(User,verbose_name=u'作者',null=True,blank=True)
    catelog = models.ForeignKey(Catelog,verbose_name=u'分类',help_text=u'指定文章发表到哪个分类')
    blog = models.ForeignKey(Blog,verbose_name=u'发表到',null=True,blank=True,help_text=u'选择这篇文章发表到哪个博客上')
    create_at = models.DateTimeField(u'创建时间',auto_now_add=True)
    status = models.IntegerField(u'设置为',choices=ENTRY_STATUS,default=1,help_text=u'存为草稿暂时不被大家看到')
    last_update_at = models.DateTimeField(u'上次修改时间',auto_now=True)
    comment_enable = models.BooleanField(u'允许评论',default=True)
    ip = models.IPAddressField(u'所在IP',editable=False,default='127.0.0.1')
    comment_count = models.IntegerField(u'评论数',editable=False,default=0)
    editor_type = models.IntegerField(u'编辑器类型',default=1,editable=False,null=True)
    last_update_by = models.CharField(u'最后更新人',max_length=20,null=True,blank=True)
    tag_str = models.CharField(u'标签',max_length=200,null=True,blank=True,help_text=u'使用空格隔开标签，如“节日 汽球 家庭”')
    
    def __unicode__(self):
        return self.title
        
    class Meta:
       verbose_name = u'文章'
       verbose_name_plural = u'文章'

#-------------------------------------------------------------------------------
class Comment(models.Model):
    COMMENT_STATUS = (
        (0,u'隐藏'),
        (1,u'显示')
    )
    title = models.CharField(u'标题',max_length=100,blank=True)
    content = models.TextField(u'内容')
    comment_to = models.ForeignKey(Entry,verbose_name=u'文章')
    blog = models.ForeignKey(Blog,verbose_name=u'博客')
    author = models.ForeignKey(User,verbose_name=u'作者',null=True,blank=True)
    author_name = models.CharField(u'作者名',max_length=30)
    comment_time = models.DateTimeField(u'评论时间',auto_now_add=True)
    last_update_at = models.DateTimeField(u'上次修改时间',auto_now=True)
    status = models.IntegerField(u'状态',choices=COMMENT_STATUS,default=1)
    ip = models.IPAddressField(u'所在IP',blank=True,null=True)
    link = models.URLField(u'连接',max_length=500,blank=True,null=True)
    
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = u'评论'
#-------------------------------------------------------------------------------
class TagManager(models.Manager):
    def get_or_create(self,tag,blog):
        try:
            item = super(TagManager, self).get_query_set().get(name=tag,blog=blog)
        except ObjectDoesNotExist:
            item = self.model(name=tag,blog=blog,entryCount=0)
        return item

    def save_tags(self,tags,entry):
        '''为一篇文章增加一系列标签'''
        for tag in tags:
            tag_object = self.get_or_create(tag,entry.blog)
            tag_object.entryCount = tag_object.entryCount + 1
            tag_object.save()
            tag_object.entrys.add(entry)
    def remove_tags(self,tags,entry):
        '''移除一篇文章的一系列标签'''
        for tag in tags:
            tag_object = self.get_or_create(tag,entry.blog)
            tag_object.entryCount = tag_object.entryCount - 1
            if tag_object.entryCount <= 0:
                tag_object.delete()
            else:
                tag_object.save()

class Tag(models.Model):
    name = models.CharField(u'标签',max_length=20)
    blog = models.ForeignKey(Blog,verbose_name=u'所属博客',help_text=u'该标签添加到哪个博客')
    entrys = models.ManyToManyField(Entry,verbose_name=u'相关文章',help_text=u'设置与本标签相关联的文章 ')
    entryCount = models.IntegerField(u'文章数',editable=False)
    
    objects = TagManager()
    
    def __unicode__(self):
        return self.name
    
    def level(self):
        l = self.entryCount / 2
        if l > 5:
            l = 5
        return l
    
    class Meta:
        verbose_name = u'标签'
        verbose_name_plural = u'标签'
#-------------------------------------------------------------------------------
class Link(models.Model):
    caption = models.CharField(u'标题',max_length=50,help_text=u'链接文字')
    link = models.CharField(u'链接',max_length=200,help_text=u'链接地址')
    order = models.IntegerField(u'顺序',default=0)
    blog = models.ForeignKey(Blog,verbose_name=u'所属博客',help_text=u'链接添加到哪个博客')
    
    def __unicode__(self):
        return self.caption
    
    class Meta:
        verbose_name = u'链接'
        verbose_name_plural = u'链接'
        
#-------------------------------------------------------------------------------
class Panelinstance(models.Model):
    PANEL_STATUS = (
        (0,u'未激活'),
        (1,u'已激活')
    )
    title = models.CharField(u'标题',max_length=50,help_text=u'标题将在页面上显示')
    panel = models.ForeignKey('Panel',verbose_name=u'面板模板',help_text=u'选择面板模板',limit_choices_to={'status__in':(0,1)})
    blog = models.ForeignKey(Blog,verbose_name=u'所属博客')
    parameters = models.TextField(u'HTML代码',null=True,blank=True,help_text=u'仅HTML面板需要填入HTML代码')
    column = models.IntegerField(u'所在列',help_text=u'面板添加到侧栏的其中一列，从左往右数从0起')
    row = models.IntegerField(u'所在行',help_text=u'面板添加到侧栏的行，从上到下数从0起')
    
    def __unicode__(self):
        return '%s on %s' % (self.panel.name,self.blog.caption)
    class Meta:
        verbose_name = u'面板'
        verbose_name_plural = u'面板'

#-------------------------------------------------------------------------------
class Panel(models.Model):
    PANEL_STATUS = (
        (0,u'不安装'),
        (1,u'安装')
    )

    name = models.CharField(u'名称',max_length=50)
    status = models.IntegerField(u'使用规则',default=0,choices=PANEL_STATUS,help_text='用户创建博客时是否安装该面板到其博客')
    template = models.TextField(u'模板',null=True,blank=True,help_text=u'目前仅支持Django的模板')
    method = models.CharField(u'函数',max_length=200,null=True,blank=True,help_text=u'面板处理函数的全名,格式为“模块名：函数名”，如\'fallever.blog.views.panels:html\'')
    scope = models.IntegerField(u'范围',default=0,editable=False) 
    share = models.BooleanField(u'共享',default=True,editable=False)
    
    def __unicode__(self):
        return self.name
    
    def create_instance(self,blog,col,row):
        pi = Panelinstance(title=self.name,panel=self,blog=blog,column=col,row=row)
        pi.save()

    class Meta:
        verbose_name = u'面板模板'
        verbose_name_plural = u'面板模板'

#------------------signals----------------------
# 文章保存后，处理标签。
def post_entry_save(sender,instance,created,**kwargs):
    tag_str = instance.tag_str or ' '
    tags = filter(lambda t:t != '',tag_str.split(' '))
    # 如果刚创建文章，直接保存标签、修改分类文章数即可。
    if created:
        Tag.objects.save_tags(tags,instance)
        
        instance.catelog.entryCount += 1
        instance.catelog.save()
    # 修改了文章，将tag_str与原有的标签对比再处理。
    else:
        old_tags = map(lambda t:t.name,instance.tag_set.all())
        commons = filter(lambda t:t in old_tags,tags) # 这些标签是编辑前后都出现的标签
        Tag.objects.save_tags(filter(lambda t:t not in commons,tags),instance)# 这些标签是新增的标签
        Tag.objects.remove_tags(filter(lambda t:t not in commons,old_tags),instance) # 这是将要去除掉的标签

signals.post_save.connect(post_entry_save, sender=Entry)

def post_entry_delete():
    pass

# 发表评论后，文章的评论数加一
def post_comment_save(sender,instance,created,**kwargs):
    if created:
        instance.comment_to.comment_count += 1
        instance.comment_to.save()
        # 顺便发一封邮件给博主哇。

def post_comment_delete():
    pass
signals.post_save.connect(post_comment_save, sender=Comment)

