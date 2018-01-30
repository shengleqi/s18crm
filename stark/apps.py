from django.apps import AppConfig


class StarkConfig(AppConfig):
    name = 'stark'
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        # 去程序中已经注册的所有app目录中找：stark.py 并执行
        autodiscover_modules('stark')
