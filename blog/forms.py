#!/usr/bin/env python
#coding=utf-8

from django import forms

class SetupForm(forms.Form):
    site_name = forms.CharField(max_length=100,required=True,label=u'站点名称')
    admin_name = forms.CharField(max_length=20,required=True,label=u'管理员名')
    admin_mail = forms.EmailField(required=True,label=u'电子邮箱')
    admin_psw = forms.CharField(max_length=20,required=True,widget=forms.PasswordInput,label=u'管理密码')
    admin_pswc = forms.CharField(max_length=20,required=True,widget=forms.PasswordInput,label=u'重复密码')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        psw = cleaned_data.get('admin_psw')
        pswc = cleaned_data.get('admin_pswc') 
        
        if psw == pswc:
            return cleaned_data
        raise forms.ValidationError(u'输入的两次密码不相同。请重新输入。')