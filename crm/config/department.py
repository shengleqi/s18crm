from stark.service import v1
from crm import models
from crm.permission import BasePermission


class DepartMentConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','title']