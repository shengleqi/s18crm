from django.shortcuts import render,redirect
from crm import models
from rbac.service import permission
from django.contrib.sessions.backends.db import SessionStore
def login(request):
    """
    用户登录
    :param request:
    :return:
    """

    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')

        # 当前用户对象
        user = models.UserInfo.objects.filter(name=user, password=pwd).first()
        if user:
            # 只要用户登录成功
            # 设置session_key
            # 权限信息放入session
            # 菜单信息放入session
            permission.init_permission(user, request)
            return redirect('/depart/')

        return render(request, 'login.html')

def reset_permission(request):
    """
    权限重置
    :param request:
    :return:
    """
    # 找到人
    # 获取这个人的session_key
    # 在session表中将该用户的数据删除。
    # name = "alex"
    # obj = models.UserInfo.objects.filter(name=name).first()
    # permission.reset_permission(obj.session_key,request)
    if request.method == "GET":
        user_list = models.UserInfo.objects.all()
        return render(request,'reset_permission.html',{'user_list':user_list})
    else:
        name = request.POST.get('name')
        obj = models.UserInfo.objects.filter(name=name).first()
        if obj.session_key:
            permission.reset_permission(obj.session_key,request)
        return redirect('/reset/permission/')
def depart(request):
    """
    部门管理
    :param request:
    :return:
    """
    return render(request,'depart.html')