#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ..service.wapper import BasePermission
from django.shortcuts import render as django_render


def render(request, template_name, context=None, permission_cls=BasePermission):
    permission = permission_cls(request.permission_codes)
    if not context:
        context = {}
    context.setdefault('permission', permission)
    return django_render(request, template_name, context)
