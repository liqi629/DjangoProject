import os
import json
from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings

from envs.models import Envs
from testcases.models import Testcases
from configures.models import Configures
from utils import common
from .models import Interfaces
from .serializers import InterfacesModelSerializer, TestcasesByInterfaceIdModelSerializer, \
    ConfiguresByInterfaceIdModelSerializer, InterfacesRunSerializer


class InterfaceViewSet(viewsets.ModelViewSet):
    '''
        create:
            创建接口

        retrieve:
            获取接口详情数据

        update:
            完整更新接口

        partial_update:
            部分更新接口

        destroy:
            删除接口

        list:
            获取接口列表数据

        testcases:
            获取接口中用例数据

        configs:
            获取接口中配置数据

        run:
            运行接口
    '''
    # 指定类属性
    queryset = Interfaces.objects.all()
    serializer_class = InterfacesModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id', 'name']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        results = response.data['results']
        data_list = []
        for item in results:
            interface_id = item['id']
            # 计算用例数
            testcases_count = Testcases.objects.filter(interface_id=interface_id).count()

            # 计算配置数
            config_count = Configures.objects.filter(interface_id=interface_id).count()

            item['testcases'] = testcases_count
            item['configures'] = config_count
            data_list.append(item)
        response.data['results'] = data_list
        return response

    @action(methods=['get'], detail=True)
    def testcases(self, request, *args, **kwargs):
        response = self.retrieve(request, *args, **kwargs)
        response.data = response.data['testcases']
        return response

    @action(methods=['get'], detail=True)
    def configs(self, request, *args, **kwargs):
        response = self.retrieve(request, *args, **kwargs)
        response.data = response.data['configures']
        return response

    @action(methods=['post'], detail=True)
    def run(self, request, *args, **kwargs):
        # 取出并构造参数
        instance = self.get_object()
        response = super().create(request, *args, **kwargs)
        env_id = response.data.serializer.validated_data.get('env_id')
        testcase_dir_path = os.path.join(settings.SUITES_DIR, datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'))
        # 创建一个以时间戳命名的路径
        os.mkdir(testcase_dir_path)
        env = Envs.objects.filter(id=env_id).first()

        testcases_qs = Testcases.objects.filter(interface=instance)
        if not testcases_qs.exists():
            data = {
                'ret': False,
                'msg': '此接口下无用例，无法运行'
            }
            return Response(data, status=400)

        for testcase_obj in testcases_qs:
            # 生成yaml用例文件
            common.generate_testcase_file(testcase_obj, env, testcase_dir_path)

        # 运行用例（生成报告）
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        if self.action == "testcases":
            return TestcasesByInterfaceIdModelSerializer
        elif self.action == "configs":
            return ConfiguresByInterfaceIdModelSerializer
        elif self.action == 'run':
            return InterfacesRunSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        if self.action == 'run':
            pass
        else:
            serializer.save()
