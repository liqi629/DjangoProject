import os
import json

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from django.conf import settings
from django.http.response import StreamingHttpResponse
from django.utils.encoding import escape_uri_path

from .models import Reports
from .serializers import ReportsModelSerializer
from .utils import get_file_content


class ReportsViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    """
    list:
        获取报告列表数据

    retrieve:
        查看报告详情

    destroy:
        删除报告

    download:
        下载报告
    """
    queryset = Reports.objects.all()
    serializer_class = ReportsModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id', 'name']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        results = response.data['results']
        data_list = []
        for item in results:
            # 将1转化为Pass，将0转化为Fail
            result = 'Pass' if item['result'] else 'Fail'
            item['result'] = result
            data_list.append(item)

        response.data['results'] = data_list
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        try:
            # 将summary json字符串转化为Python中的字典类型
            response.data['summary'] = json.loads(response.data['summary'], encoding='utf-8')
        except Exception as e:
            raise e
        return response

    @action(detail=True)
    def download(self, request, *args, **kwargs):
        # 获取html源码
        instance = self.get_object()
        html = instance.html
        name = instance.name
        # 获取测试报告所属目录路径
        report_dir = settings.REPORT_DIR
        # 生成html文件，存放到reports目录下
        report_full_dir = os.path.join(report_dir, name) + '.html'
        if not os.path.exists(report_full_dir):
            with open(report_full_dir, 'w', encoding='utf-8') as file:
                file.write(html)

        # 获取文件流，返回给前端
        # 创建一个生成器，获取文件流，每次获取的是文件字节数据
        response = StreamingHttpResponse(get_file_content(report_full_dir))
        html_file_name = escape_uri_path(name + '.html')
        # 添加响应头
        # 直接使用Response对象['响应头名称'] = '值'
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f"attachement; filename*=UTF-8''{html_file_name}"
        return response
