from django.utils.deprecation import MiddlewareMixin
import re
from django.shortcuts import HttpResponse
from django.conf import settings


class RbacMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # 1. 获取白名单，让白名单中的所有url和当前访问url匹配
        for reg in settings.PERMISSION_VALID_URL:
            if re.match(reg, request.path_info):
                return None

        # 2. 获取权限
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if not permission_dict:
            return HttpResponse('未获取到当前用户的权限信息或权限被重置，请重新登录')

        flag = False
        # 3. 对用户请求的url进行匹配
        for value in permission_dict.values():
            urls = value['urls']
            codes = value['codes']
            # 循环每一个url，当有url匹配成功后，将当前组的所有的codes赋值给request.permission_codes，以便在前端使用
            for reg in urls:
                regx = "^%s$" % (reg,)
                if re.match(regx, request.path_info):
                    request.permission_codes = codes # ['list','add','edit','del']
                    flag = True
                    break
            if flag:
                break

        if not flag:
            return HttpResponse('无权访问')
