from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from crm.permission import BasePermission
from stark.service import v1
from crm import models

class SchoolConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','title']
