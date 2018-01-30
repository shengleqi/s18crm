from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from crm.permission import BasePermission



from stark.service import v1
from crm import models
from crm.config import department
from crm.config import userinfo
from crm.config import classlist
from crm.config import course
from crm.config import customer
from crm.config import school
from crm.config import student

v1.site.register(models.Department,department.DepartMentConfig)

v1.site.register(models.UserInfo,userinfo.UserInfoConfig)

v1.site.register(models.Course,course.CourseConfig)

v1.site.register(models.School,school.SchoolConfig)

v1.site.register(models.ClassList,classlist.ClassListConfig)

v1.site.register(models.Customer,customer.CustomerConfig)


v1.site.register(models.Student,student.StudentConfig)

