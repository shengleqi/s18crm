#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import copy
from django.template import Library
from django.conf import settings

register = Library()


@register.inclusion_tag('rbac/menu.html')
def menu_html(request):
    """
    生成菜单
    :param request: 
    :return: 
    """
    menu_list = request.session.get(settings.MENU_LIST_SESSION_KEY)
    if not menu_list:
        raise Exception('Session无当前用户的菜单信息')

    menu_list = copy.deepcopy(menu_list)
    flag = False
    for item in menu_list:
        for child in item['children']:
            for regex in child['regex_list']:
                regex = "^{0}$".format(regex)
                if re.match(regex, request.path_info):
                    flag = True
                    break
            if flag:
                child['class'] = 'active'
                break
        if flag:
            item['class'] = ''
            break
    return {'menu_list': menu_list}
