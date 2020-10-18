from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls
# from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Lemon API接口文档平台",  # 必传
        default_version='v1',  # 必传
        # description="这是一个美轮美奂的接口文档",
        # terms_of_service="http://api.keyou.site",
        # contact=openapi.Contact(email="keyou100@qq.com"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    # permission_classes=(permissions.AllowAny,), # 权限类
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='测试平台接口文档')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schemaredoc'),
    path('api/', include('rest_framework.urls')),
    path('user/', include('users.urls')),
    path('', include('projects.urls')),
    path('', include('interfaces.urls')),
    path('', include('envs.urls')),
    path('', include('debugtalks.urls')),
    path('', include('testsuits.urls')),
    path('', include('reports.urls')),
    path('', include('testcases.urls')),
    path('', include('configures.urls')),
    path('', include('summary.urls')),
]
