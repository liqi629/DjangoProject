import json

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from rest_framework.response import Response

from .models import Configures
from . import serializers
from utils import handle_datas
from interfaces.models import Interfaces


class ConfiguresViewSet(ModelViewSet):
    """
        create:
            创建配置

        retrieve:
            获取配置详情数据

        update:
            完整更新配置

        partial_update:
            部分更新配置

        destroy:
            删除配置

        list:
            获取配置列表数据

        """
    queryset = Configures.objects.all()
    serializer_class = serializers.ConfiguresModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ('id', 'name')

    def retrieve(self, request, *args, **kwargs):
        """获取配置详情信息"""
        # Testcase对象
        testcase_obj = self.get_object()

        # 用例请求信息
        testcase_request = json.loads(testcase_obj.request, encoding='utf-8')
        testcase_request_datas = testcase_request.get('config').get('request')

        # 处理用例的header列表
        testcase_headers = testcase_request_datas.get('headers')
        testcase_headers_list = handle_datas.handle_data4(testcase_headers)

        # 处理用例variables变量列表
        testcase_variables = testcase_request.get('config').get('variables')
        testcase_variables_list = handle_datas.handle_data2(testcase_variables)

        selected_interface_id = testcase_obj.interface_id
        selected_project_id = Interfaces.objects.get(id=selected_interface_id).project_id

        datas = {
            "author": testcase_obj.author,
            "testcase_name": testcase_obj.name,
            "selected_interface_id": selected_interface_id,
            "selected_project_id": selected_project_id,
            "header": testcase_headers_list,
            "globalVar": testcase_variables_list,  # 变量

        }
        return Response(datas)
