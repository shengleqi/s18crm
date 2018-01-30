from django.db import models


class Menu(models.Model):
    """
    一级菜单表
    """
    title = models.CharField(verbose_name='菜单标题', max_length=32)


class PermissionGroup(models.Model):
    """
    权限组
    """
    caption = models.CharField(verbose_name='权限组名称', max_length=32)
    menu = models.ForeignKey(verbose_name='所属菜单', to='Menu', default=1)


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)
    code = models.CharField(verbose_name='权限代号', max_length=32)
    group = models.ForeignKey(verbose_name='所属组', to='PermissionGroup')

    parent = models.ForeignKey(to='Permission', related_name='ps', null=True)

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色
    """
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)

    def __str__(self):
        return self.title


class User(models.Model):
    """
    用户表
    """
    name = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to=Role)

    session_key = models.CharField(verbose_name='当前登录用户的session_key', max_length=40, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
