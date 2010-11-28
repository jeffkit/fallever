def blog_context(request):
    panels = blog.panelinstance_set.filter(blog=blog).select_related(depth=1).order_by('column').order_by('row')
    