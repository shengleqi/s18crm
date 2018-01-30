from types import FunctionType

from django.conf.urls import url
from django.forms import ModelForm
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from stark.utils.pager import Pagination

"""
迭代器：有next方法
生成器：yield就是生成器；有next方法； -> 也是一种迭代器
可迭代对象：类中有__iter__方法且该方法返回一个 迭代器
"""
# 1. 如果一个对象是，是可迭代对象就可以被for循环
# 2. 如何让对象变成可迭代对象？
import copy
class FilterRow(object):

    def __init__(self,queryset,name,request_get,changelist_url,is_choice=False):
        """
        :param data: queryset类型
        :param name: 字段名称
        :param request_get: get穿过来的参数 gender=1&dp=2&status=1
        :param changelist_url: 当前列表页面的url
        """
        self.queryset = queryset
        self.is_choice = is_choice
        self.name = name
        self.changelist_url = changelist_url
        self.params = copy.deepcopy(request_get)
        self.params._mutable = True


    def __iter__(self):
        # self.params, QueryDict,   urlencode = > dp=2&status=1

        if self.name in self.params:
            oldval = self.params.get(self.name)
            self.params.pop(self.name)
            yield mark_safe(
                "<a href='{0}?{1}'>全部</a>".format(self.changelist_url, self.params.urlencode()))
        else:
            oldval = None
            yield mark_safe("<a class='active' href='{0}?{1}'>全部</a>".format(self.changelist_url,self.params.urlencode()))

        for obj in self.queryset:
            if self.is_choice:
                nid = str(obj[0])
                text = obj[1]
            else:
                nid = str(obj.pk)
                text = str(obj)
            self.params[self.name] = nid

            if oldval == nid:
                yield mark_safe("<a class='active' href='{0}?{1}'>{2}</a>".format(self.changelist_url,self.params.urlencode(),text))
            else:
                yield mark_safe(
                    "<a href='{0}?{1}'>{2}</a>".format(self.changelist_url, self.params.urlencode(),
                                                                      text))

class ChangeList(object):
    """
    用于对列表页面的功能做拆分
    """
    def __init__(self,config,result_list,request):
        """
        :param config: 处理每个表增伤改查功能的对象
        :param result_list: 从数据库查询到的数据
        """
        self.config = config # get_changlist_url
        self.request = request

        self.search_list = config.search_list
        self.search_value = request.GET.get('key','')

        self.action_list = config.action_list
        self.comb_filter = config.comb_filter

        self.show_add_btn = config.get_show_add_btn()


        all_count = result_list.count()
        page_obj = Pagination(request.GET.get('page'), all_count, request.path_info,request.GET)

        if result_list:
            self.result_list = result_list[page_obj.start:page_obj.end]
        else:
            self.result_list = result_list
        self.page_obj = page_obj

    def header_list(self):
        """
        处理页面表头的内容
        :return:
        """
        result = []
        # ['id', 'name', 'email',display_edit,display_del]
        # ['ID', '用户名', '邮箱','临时表头',临时表头]

        for n in self.config.get_list_display():
            if isinstance(n, FunctionType):
                # 执行list_display中的函数
                val = n(self.config, is_header=True)
            else:
                val = self.config.mcls._meta.get_field(n).verbose_name
            result.append(val)

        return result

    def body_list(self):
        """
        处理页面表内容
        :return:
        """
        result = []
        """
        [
            obj,
            obj,
            obj,
        ]
        # ['id', 'name', 'email',display_edit,display_del]
        [
            [1, '天了','123@liv.com'],
            [2, '天1了','123@liv.com'],
            [3, '天了123','123@liv.com'],
        ]
        """
        for row in self.result_list:
            temp = []
            for n in self.config.get_list_display():
                if isinstance(n, FunctionType):
                    val = n(self.config, row=row)
                else:
                    val = getattr(row, n)
                temp.append(val)
            result.append(temp)
        return result

    def add_url(self):
        """
        生成添加按钮
        :return:
        """
        # 处理添加按钮的URL
        # self.mcls
        app_model_name = (self.config.mcls._meta.app_label, self.config.mcls._meta.model_name,)
        name = "stark:%s_%s_add" % app_model_name
        add_url = reverse(name)
        return add_url

    def show_comb_search(self):
        # self.comb_filter # ['gender','status','dp']
        # "gender"，找类中的gender字段对象，并将其对象中的choice获取
        # "status"，找类中的status字段对象，并将其对象中的choice获取
        # "dp"，找类中的dp字段对象，并将其关联的表中的所有数据获取到
        from django.db.models.fields.related import ForeignKey
        for name in self.comb_filter:
            _field = self.config.mcls._meta.get_field(name)
            changelist_url = self.config.get_changlist_url()
            if type(_field) == ForeignKey:
                yield FilterRow(_field.rel.to.objects.all(),name,self.request.GET,changelist_url)
            else:
                yield FilterRow(_field.choices,name,self.request.GET,changelist_url,is_choice=True)

class StarkConfig(object):
    """
    用于封装  单独数据库操作类
    """
    def display_checkbox(self,is_header=False,row=None):
        if is_header:
            return '选择'
        return mark_safe("<input type='checkbox' name='pk' value='%s' />" %(row.id,))

    def display_edit(self, is_header=False, row=None):
        if is_header:
            return "编辑"
        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
        name = "stark:%s_%s_change" % app_model_name
        url_path = reverse(name, args=(row.id,))
        return mark_safe('<a href="%s">编辑</a>' % (url_path,))

    def display_del(self, is_header=False, row=None):
        if is_header:
            return "删除"

        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
        name = "stark:%s_%s_delete" % app_model_name
        url_path = reverse(name, args=(row.id,))
        return mark_safe('<a href="%s">删除</a>' % (url_path,))

    show_add_btn = True
    def get_show_add_btn(self):
        return self.show_add_btn

    list_display = []
    def get_list_display(self):
        result = []
        if self.list_display:
            result.extend(self.list_display)
            result.insert(0,StarkConfig.display_checkbox)
            result.append(StarkConfig.display_edit)
            result.append(StarkConfig.display_del)
        return result

    model_form_cls = None
    def get_model_form_cls(self):
        """
        如果类中定义了 model_form_cls，则使用；否则创建TempModelForm
        :return:
        """
        if self.model_form_cls:
            return self.model_form_cls

        class TempModelForm(ModelForm):
            class Meta:
                model = self.mcls
                fields = "__all__"


        return TempModelForm

    search_list = []

    action_list = []

    comb_filter = []

    def __init__(self,mcls):
        self.mcls = mcls

    @property
    def urls(self):
        # self = StarkConfig(models.UserInfo) # obj.mcls = models.UserInfo
        # StarkConfig(models.Role),# # obj.mcls = models.Role

        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)

        patterns =[
            url(r'^$',self.changelist_view,name='%s_%s_changelist' %app_model_name),
            url(r'^add/$',self.add_view,name='%s_%s_add'  %app_model_name),
            url(r'^(\d+)/change/$',self.change_view,name="%s_%s_change"  %app_model_name),
            url(r'^(\d+)/delete/$',self.delete_view,name="%s_%s_delete"  %app_model_name),
        ]

        patterns.extend(self.extra_url())

        return patterns

    # ############# 反向生成URL开始 ##################
    def get_edit_url(self,pk):
        # /stark/app01/userinfo/1/change/
        # /stark/app02/role/1/change/
        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
        name = "stark:%s_%s_change"  %app_model_name
        url_path = reverse(name,args=(pk,))
        return url_path

    def get_delete_url(self,pk):
        # /stark/app01/userinfo/1/delete/
        # /stark/app02/role/1/delete/
        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
        name = "stark:%s_%s_delete"  %app_model_name
        url_path = reverse(name,args=(pk,))
        return url_path

    def get_changlist_url(self):
        # /stark/app01/userinfo/1/delete/
        # /stark/app02/role/1/delete/
        app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
        name = "stark:%s_%s_changelist"  %app_model_name
        url_path = reverse(name)
        return url_path

    # ############# 反向生成URL结束 ##################

    def extra_url(self):
        """
        钩子函数
        :return:
        """
        return []

    def get_key_search_condtion(self,request):
        from django.db.models import Q
        key = request.GET.get('key')  # 小偷 -> 构造or条件
        con = Q()
        con.connector = 'OR'
        if key:
            for name in self.search_list:
                con.children.append((name, key,))
        return con

    def get_comb_filter_condition(self,request):
        comb_condition = {}
        for name in self.comb_filter:
            val = request.GET.get(name)
            if not val:
                continue
            comb_condition[name] = val
        return comb_condition

    def changelist_view(self,request):
        """
        列表页面
        :param request:
        :return:
        """
        self.request = request


        if request.method == 'POST':
            action = request.POST.get('xxxx') # multi_install / multi_monitor
            func_name = getattr(self,action,None)
            if func_name:
                response = func_name(request)
                if response:
                    return response

        result_list = self.mcls.objects.filter(self.get_key_search_condtion(request)).filter(**self.get_comb_filter_condition(request))

        cl = ChangeList(self,result_list,request)

        return render(request, 'stark/changelist.html', {'cl':cl})

    def add_view(self,request):
        """
        添加页面
        :param request:
        :return:
        """
        self.request = request

        model_form_class = self.get_model_form_cls()

        if request.method == "GET":
            form = model_form_class()
            return render(request, 'stark/add_view.html', {'form':form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                # 跳转到列表页面
                app_model_name = (self.mcls._meta.app_label, self.mcls._meta.model_name,)
                name = "stark:%s_%s_changelist" % app_model_name
                list_url = reverse(name)
                return redirect(list_url)

            return render(request, 'stark/add_view.html', {'form': form})

    def change_view(self,request,nid):
        """
        编辑页面
        :param request:
        :param nid:
        :return:
        """
        self.request = request

        obj = self.mcls.objects.filter(pk=nid).first()
        if not obj:
            return HttpResponse('别闹')

        model_form_cls = self.get_model_form_cls()
        if request.method == "GET":
            form = model_form_cls(instance=obj)
            return render(request, 'stark/change_view.html', {'form':form})
        else:
            form = model_form_cls(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_changlist_url())
            return render(request, 'stark/change_view.html', {'form': form})

    def delete_view(self,request,nid):

        self.request = request

        self.mcls.objects.filter(id=nid).delete()
        path = self.get_changlist_url()
        return redirect(path)

class StarkSite(object):
    """
    用于封装所有的   数据库操作类
    """
    def __init__(self):
        self._registry = {}

    def register(self,model_class,config_cls=None):
        # models.UserInfo,UserInfoConfig
        if not config_cls:
            config_cls = StarkConfig
        self._registry[model_class] = config_cls(model_class)

    @property
    def urls(self):
        from django.conf.urls import url
        pts = [
            url(r'^login/', self.login),
        ]
        """
        _registry = {
            models.UserInfo: StarkConfig(models.UserInfo),
            models.Role: StarkConfig(models.Role),
        }
        
        # /admin//app01/userinfo/           查看列表页面
        # /admin/app01/userinfo/add/        添加页面
        # /admin/app01/userinfo/1/change/   修改页面
        # /admin/app01/userinfo/1/delete/   删除页面
        
        
        /stark/   ->  ([
                            /login/
                            /app01/userinfo/  --> ([
                                                        /                    查看列表
                                                        add/                 添加
                                                        (\d+)/change/        修改
                                                        (\d+)/delete/        删除
                                                    ])
                            /app01/role/
                                                --> ([
                                                        /                   查看列表
                                                        add/                添加
                                                        (\d+)/change/        修改
                                                        (\d+)/delete/        删除
                                                    ])
                        ])

        """
        for model_class,config_obj in self._registry.items():
            """
            _registry = {
                models.UserInfo: StarkConfig(models.UserInfo)，# 对象对象对象
                models.Role: StarkConfig(models.Role),# 对象对象对象
            }
            """
            app_label = model_class._meta.app_label
            model_name = model_class._meta.model_name
            # models.UserInfo: StarkConfig(models.UserInfo) # obj.mcls = models.UserInfo
            # config_obj.urls，对象的urls方法

            # models.Role: StarkConfig(models.Role),# # obj.mcls = models.Role
            # config_obj.urls，对象的urls方法
            temp = url(r'^%s/%s/' %(app_label,model_name), (config_obj.urls,None,None))
            pts.append(temp)

        return pts,None,"stark"

    def login(self,request):
        return HttpResponse('登录页面')

site = StarkSite()