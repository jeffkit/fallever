#!/usr/bin/env python
#coding=utf-8
from django import template
from django.template import resolve_variable

menus = (
    ['首页',"/home/",[
        ["欢迎","/home/"]
    ]],
    ["文章","/entrys/",[
        ["管理","/entrys/"],
        ["发表","/entry/new/,/entry/post/,/entry/edit/"],
        ["评论","/comments/"]
    ]],
    ["设置","/settings/",[]],
    ["外观","/lookandfeel/",[]]
)


class Menu:
    def __init__(self,name,url,parent,current):
        self.name = name
        self.url = url
        self.parent = parent
        self.current = current
    def __str__(self):
        return "%s's current is %s"%(self.name,self.current)

def build_menu(name,url,curl,parent):
    current = False
    if ',' in url:
        urls = url.split(',')
        url = urls[0]
        for u in urls:
            if curl.startswith(u):
                current = True
                break
    if not current:
        current = curl.startswith(url)
    menu = Menu(name,url,parent,current)
    return menu
    
#根据一个元组生成菜单
def create_menu(mt,curl):
    result = []
    for ar in mt:
        menu = build_menu(ar[0],ar[1],curl,None)
        children = []
        for suar in ar[2]:
            child = build_menu(suar[0],suar[1],curl,menu)
            if child.current:
                menu.current = True            
            children.append(child)
            result.append(child)
        menu.children = children
        result.append(menu)
    return result
    
def get_top_menus(menus):
    for menu in menus:
        if not menu.parent:
            yield menu
            
#生成Html文本供输出
def generate_html(menus,shortcut):
    html = "<div id=\"nav_wrap\">\n\t<ul id=\"nav\">\n"
    cm = None
    for menu in get_top_menus(menus):
        cls = ""
        if menu.current:
            cls += "class=\"current\""
            cm = menu
        html += "\t\t<li><a href=\"/blogmgmt/%s%s\" %s>%s</a></li>\n"%(shortcut,menu.url,cls,menu.name)
    html += "\t</ul>\n</div>\n"
    html += "<div id=\"subnav_wrap\">\n"
    if cm and cm.children:
        html += "\t<ul id=\"subnav\">\n"
        for sub in cm.children:
            cls = ""
            if sub.current:
                cls += "class=\"current\""
            html += "\t\t<li><a href=\"/blogmgmt/%s%s\" %s>%s</a></li>\n"%(shortcut,sub.url,cls,sub.name)
        html += "\t</ul>\n"
    html += "</div>\n"
    
    return html


class NavigatorNode(template.Node):
    def __init__(self, url,shortcut):
        self.url = url
        self.shortcut = shortcut
    def render(self, context):
        path = resolve_variable(self.url, context)
        sc = resolve_variable(self.shortcut, context)
        path = path[len('/blogmgmt/') + len(sc):]
        return generate_html(create_menu(menus,path),sc)

def navigator(parser,token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, url, shortcut = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return NavigatorNode(url,shortcut)

register = template.Library()
register.tag('navigator',navigator)


#print generate_html(create_menu(menus,'/comments/'))
