import os
import json
from datetime import datetime

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings

from interfaces.models import Interfaces
from .models import Testsuits
from envs.models import Envs
from testcases.models import Testcases
from .serializers import TestsuitsModelSerializer, TestsuitsRunSerializer
from utils import common


class TestsuitsViewSet(ModelViewSet):
    """
        create:
            创建套件

        retrieve:
            获取套件详情数据

        update:
            完整更新套件

        partial_update:
            部分更新套件

        destroy:
            删除套件

        list:
            获取套件列表数据

        run:
            运行套件
        """
    queryset = Testsuits.objects.all()
    serializer_class = TestsuitsModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id', 'name']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'name': instance.name,
            'project_id': instance.project_id,
            'include': instance.include
        }
        return Response(data)

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

        testsuit_include = json.loads(instance.include, encoding='utf-8')
        testcases_qs_list = []
        for interface_id in testsuit_include:
            testcases_qs = Testcases.objects.filter(interface_id=interface_id)
            testcases_qs_list.extend(list(testcases_qs))

        if len(testcases_qs_list) == 0:
            data = {
                'ret': False,
                'msg': '此套件下无用例，无法运行'
            }
            return Response(data, status=400)

        for testcase_obj in testcases_qs_list:
            # 生成yaml用例文件
            common.generate_testcase_file(testcase_obj, env, testcase_dir_path)

        # 运行用例（生成报告）
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        if self.action == 'run':
            return TestsuitsRunSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        if self.action == 'run':
            pass
        else:
            serializer.save()
