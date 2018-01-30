#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.conf import settings


def init_permission(user, request):
    """
    权限信息初始化
    :param user: 用户对象 
    :param request: 请求相关
    :return: 
    """

    # 用户登录成功，获取当前用户所有的权限
    permission_list = user.roles.filter(
        permissions__title__isnull=False
    ).values('permissions__id',  # 权限ID
             'permissions__title',  # 权限标题
             'permissions__group_id',  # 权限所在的组ID
             'permissions__code',  # 权限代号
             'permissions__parent_id',  # 权限代号
             'permissions__group__menu__title',  # 权限代号
             'permissions__group__menu__id',  # 权限代号
             'permissions__url').distinct()

    # ########### 用于做权限的验证 ###########
    permission_dict = {}
    for item in permission_list:
        group_id = item['permissions__group_id']
        if group_id in permission_dict:
            permission_dict[group_id]['urls'].append(item['permissions__url'])
            permission_dict[group_id]['codes'].append(item['permissions__code'])
        else:
            permission_dict[group_id] = {
                'urls': [item['permissions__url'], ],
                'codes': [item['permissions__code'], ]
            }

    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict

    # ########### 用于做菜单 ###########
    menu_dict = {}
    for item in permission_list:
        pid = item['permissions__parent_id']
        nid = item['permissions__id']
        if pid:
            continue
        menu_dict[nid] = {
            'menu__id': item['permissions__group__menu__id'],
            'menu__title': item['permissions__group__menu__title'],
            'title': item['permissions__title'],
            'url': item['permissions__url'],
            'class': '',
            'regex_list': [item['permissions__url'], ]
        }

    for item in permission_list:
        pid = item['permissions__parent_id']
        if not pid:
            continue
        url = item['permissions__url']
        menu_dict[pid]['regex_list'].append(url)

    result = {}
    for row in menu_dict.values():
        menu_id = row.pop('menu__id')
        menu_title = row.pop('menu__title')
        if menu_id in result:
            result[menu_id]['children'].append(row)
        else:
            result[menu_id] = {
                'title': menu_title,
                'class': 'hide',
                'children': [
                    row,
                ]
            }
    menu_list = list(result.values())
    request.session[settings.MENU_LIST_SESSION_KEY] = menu_list


    # 获取当前用户的session_key,并保存到用户表
    user.session_key = request.session.session_key
    user.save()


def reset_permission(session_key, request):
    """
    根据session_key，删除session中保存的信息，以此来设置修改权限后需要重新登录。
    :param session_key: 被修改权限的用户session_key
    :return: 
    """
    request.session.delete(session_key)
