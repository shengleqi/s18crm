from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from crm.permission import BasePermission
from stark.service import v1
from crm import models


class ClassListConfig(BasePermission,v1.StarkConfig):

    def display_course(self,row=None,is_header=False):
        if is_header:
            return '课程'
        return "%s(%s期)" %(row.course.name,row.semester,)

    list_display = ['school',display_course,'price']
