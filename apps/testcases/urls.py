from rest_framework.routers import SimpleRouter, DefaultRouter

from . import views

# 定义路由对象
router = DefaultRouter()
router.register(r'testcases', views.TestcasesViewSet)

urlpatterns = [

]
urlpatterns += router.urls
