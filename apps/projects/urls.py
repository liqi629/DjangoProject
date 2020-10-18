from rest_framework.routers import DefaultRouter, SimpleRouter

from projects import views

# 注册路由
router = DefaultRouter()
router.register(r'projects', views.ProjectsViewSet)
urlpatterns = []
urlpatterns += router.urls
