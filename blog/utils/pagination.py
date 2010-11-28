#!/usr/bin/env python
#coding=utf-8

class Pager:
    page_def = 1
    maxlength_def = 7
    def __init__(self,datas,total,page=page_def,maxlength=maxlength_def):
        if page < 1:
            self.page = 1
        if maxlength < 1:
            self.maxlength = 10
        self.datas = datas
        self.total = total
        self.page = page
        self.maxlength = maxlength
        self.first_page = 1
        self.last_page = (self.total / self.maxlength) + 1
        if self.page > 1:
            self.pre_page = self.page - 1
        else:
            self.pre_page = self.page
        if self.page < self.last_page:
            self.next_page = self.page + 1
        else:
            self.next_page = self.page
        
        self.is_begin,self.is_end = False,False
        if self.page == self.first_page:
            self.is_begin = True
        if self.page == self.last_page:
            self.is_end = True

def test():
    page = Pager(None,35)
    print page.page
    print page.maxlength
    print page.first_page
    print page.last_page
    print page.pre_page
    print page.next_page
    print page.is_begin
    print page.is_end

#test()

