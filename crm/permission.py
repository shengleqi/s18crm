from stark.service import v1
class BasePermission(object):
    # 控制页面是否显示添加按钮
    def get_show_add_btn(self):
        # 'add' in request.permission_codes
        # True
        # False
        if 'add' in self.request.permission_codes:
            return True

    # 控制页面显示的列
    def get_list_display(self):
        result = []
        if self.list_display:
            result.extend(self.list_display)
            result.insert(0, v1.StarkConfig.display_checkbox)
            # 'edit' in request.permission_codes
            if 'edit' in self.request.permission_codes:
                result.append(v1.StarkConfig.display_edit)
            if 'del' in self.request.permission_codes:
                result.append(v1.StarkConfig.display_del)
        return result