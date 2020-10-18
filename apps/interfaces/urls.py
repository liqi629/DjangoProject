from rest_framework.routers import DefaultRouter, SimpleRouter

from interfaces import views

# 注册路由
router = DefaultRouter()
router.register(r'interfaces', views.InterfaceViewSet)
urlpatterns = []
urlpatterns += router.urls
