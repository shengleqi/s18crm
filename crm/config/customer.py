from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from crm.permission import BasePermission
from stark.service import v1
from crm import models


class CustomerConfig(BasePermission,v1.StarkConfig):

    def display_status(self,row=None,is_header=False):
        if is_header:
            return '状态'
        return row.get_status_display()

    def display_course(self,row=None,is_header=False):
        if is_header:
            return '咨询课程'
        # [Course对象，Course对象，Course对象，]
        course_list = row.course.all()

        text_list = []
        for item in course_list:
            temp = "<span style='display:inline-block;padding:3px;border:1px solid red;margin:0 2px;'>%s</span>" %(item.name,)
            text_list.append(temp)
        return mark_safe("".join(text_list))

    def display_check(self,row=None,is_header=False):
        if is_header:
            return '检查'
        return mark_safe("<a href='http://www.xxxx.com?nid=%s'>点我</a>" %(row.id,))

    list_display = ['id','qq','name',display_course,display_status,display_check]

    # 搜索
    search_list = ['qq','name__contains']

    # 组合搜索
    comb_filter = ['gender', 'status']


    # 自定义视图函数
    def extra_url(self):
        patterns = [
            url(r'^user/$', self.user_view),
        ]
        return patterns

    def user_view(self,request):
        # current_user_id = request.session['user_info']['nid']
        current_user_id = 3
        customer_list = models.Customer.objects.filter(consultant=current_user_id)
        return render(request,'customer_user.html',{'customer_list':customer_list})
