from stark.service import v1
from crm.permission import BasePermission


class StudentConfig(BasePermission,v1.StarkConfig):
    list_display = ['id','username','emergency_contract']