"""
分页组件：
    使用方法：
        视图函数：
            from utils.pager import Pagination
            def host(request):
                all_count = models.Host.objects.all().count()

                page_obj = Pagination(request.GET.get('page'),all_count,request.path_info)

                host_list = models.Host.objects.all()[page_obj.start:page_obj.end]

                return render(request,'host.html',{'host_list':host_list,'page_html':  page_obj.page_html()})
        HTML：
            <style>
                .pager a{
                    display: inline-block;
                    padding: 3px 5px;
                    margin: 0 3px;
                    border: 1px solid #dddddd;
                }
                .pager a.active{
                    background-color: cadetblue;
                    color: white;
                }

            </style>

            <div class="pager">
                {{ page_html}}
            </div>




"""


from django.utils.safestring import mark_safe
import copy


class Pagination(object):
    def __init__(self,current_page,total_count,base_url,request_get, per_page_count=10,max_pager_num=11):
        """
        :param current_page: 用户请求的当前页
        :param per_page_count: 每页显示的数据条数
        :param total_count:  数据库中查询到的数据总条数
        :param max_pager_num: 页面上最多显示的页码
        """
        self.base_url = base_url
        total_page_count, div = divmod(total_count, per_page_count)
        if div:
            total_page_count += 1

        self.total_page_count = total_page_count
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        if current_page > total_page_count:
            current_page = total_page_count

        self.current_page = current_page
        self.per_page_count = per_page_count
        self.total_count = total_count
        self.max_pager_num = max_pager_num
        self.half_max_pager_num = int(max_pager_num/2)

        self.params = copy.deepcopy(request_get)
        self.params._mutable = True

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    def bootstrap_page_html(self):
        """
        生成页码
        :return:
        """
        page_html_list = []

        if self.current_page <= 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            # {page=1&key=小偷} => page=1&key=xxxx
            self.params['page'] = self.current_page - 1
            prev = "<li><a href='%s?%s'>上一页</a></li>" % (self.base_url,self.params.urlencode(),)
        page_html_list.append(prev)

        max_pager_num = 11
        half_max_pager_num = int(max_pager_num / 2)

        # 数据总页数 < 页面上最大显示的页码个数
        if self.total_page_count <= max_pager_num:
            page_start = 1
            page_end = self.total_page_count
        else:
            # 数据比较多，已经超过11个页码
            # 如果当前页 <=5,显示 1-11
            if self.current_page <= half_max_pager_num:
                page_start = 1
                page_end = max_pager_num
            else:
                # 当前页 >=6
                if (self.current_page + 5) > self.total_page_count:
                    page_end = self.total_page_count
                    # page_start = current_page - 5
                    page_start = self.total_page_count - max_pager_num + 1
                else:
                    page_start = self.current_page - half_max_pager_num  # 当前页 - 5
                    page_end = self.current_page + half_max_pager_num  # 当前页 + 5

        for i in range(page_start, page_end + 1):
            self.params['page'] = i
            if self.current_page == i:
                tag = "<li class='active'><a href='%s?%s'>%s</a></li>" % (self.base_url,self.params.urlencode(), i,)
            else:
                tag = "<li><a href='%s?%s'>%s</a></li>" % (self.base_url,self.params.urlencode(), i,)
            page_html_list.append(tag)

        # 下一页
        if self.current_page >= self.total_page_count:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            self.params['page'] = self.current_page + 1
            nex = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url,self.params.urlencode(),)
        page_html_list.append(nex)

        return mark_safe("".join(page_html_list))

    def page_html(self):
        """
        生成页码
        :return:
        """
        page_html_list = []

        if self.current_page <= 1:
            prev = "<a href='#'>上一页</a>"
        else:
            prev = "<a href='%s?page=%s'>上一页</a>" % (self.base_url,self.current_page - 1,)
        page_html_list.append(prev)

        max_pager_num = 11
        half_max_pager_num = int(max_pager_num / 2)

        # 数据总页数 < 页面上最大显示的页码个数
        if self.total_page_count <= max_pager_num:
            page_start = 1
            page_end = self.total_page_count
        else:
            # 数据比较多，已经超过11个页码
            # 如果当前页 <=5,显示 1-11
            if self.current_page <= half_max_pager_num:
                page_start = 1
                page_end = max_pager_num
            else:
                # 当前页 >=6
                if (self.current_page + 5) > self.total_page_count:
                    page_end = self.total_page_count
                    # page_start = current_page - 5
                    page_start = self.total_page_count - max_pager_num + 1
                else:
                    page_start = self.current_page - half_max_pager_num  # 当前页 - 5
                    page_end = self.current_page + half_max_pager_num  # 当前页 + 5

        for i in range(page_start, page_end + 1):
            if self.current_page == i:
                tag = "<a class='active' href='%s?page=%s'>%s</a>" % (self.base_url,i, i,)
            else:
                tag = "<a href='%s?page=%s'>%s</a>" % (self.base_url,i, i,)
            page_html_list.append(tag)

        # 下一页
        if self.current_page >= self.total_page_count:
            nex = "<a href='#'>下一页</a>"
        else:
            nex = "<a href='%s?page=%s'>下一页</a>" % (self.base_url,self.current_page + 1,)
        page_html_list.append(nex)

        return mark_safe("".join(page_html_list))