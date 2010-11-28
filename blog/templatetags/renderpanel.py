#!/usr/bin/env python
#coding=utf-8
from django import template
from django.template import resolve_variable
from fallever.blog.models import Panel

# see http://docs.python.org/lib/built-in-funcs.html
def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class PanelNode(template.Node):
    def __init__(self, panel,request,blog):
        self.panel = panel
        self.request = request
        self.blog = blog
    def render(self, context):
        panel = resolve_variable(self.panel, context)
        
        request = resolve_variable(self.request, context)
        blog = resolve_variable(self.blog, context)
        meta = panel.panel.method.split(':')
        mod = my_import(meta[0])
        ctx = getattr(mod,meta[1])(request,panel,blog)
        tp = template.Template(panel.panel.template)
        return tp.render(ctx)
        

def renderpanel(parser,token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, panel, request,blog = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return PanelNode(panel,request,blog)

register = template.Library()
register.tag('renderpanel',renderpanel)
