from stark.service import v1
from crm import models
from crm.permission import BasePermission

class UserInfoConfig(BasePermission,v1.StarkConfig):

    def display_gender(self,row=None,is_header=False):
        if is_header:
            return '性别'
        return row.get_gender_display()

    list_display = ['id','nickname','email',display_gender]


