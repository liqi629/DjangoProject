import os
import json
from datetime import datetime

from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings

from envs.models import Envs
from testcases.models import Testcases
from testsuits.models import Testsuits
from utils import common
from .models import Projects
from interfaces.models import Interfaces
from .serializers import ProjectsModelSerializer, ProjectsNamesModelSerializer, InterfacesByProjectIdModelSerializer, \
    ProjectsRunSerializer


class ProjectsViewSet(viewsets.ModelViewSet):
    """
    create:
        创建项目

    retrieve:
        获取项目详情数据

    update:
        完整更新项目

    partial_update:
        部分更新项目

    destroy:
        删除项目

    list:
        获取项目列表数据

    names:
        返回所有项目ID和名称

    interfaces:
        返回某个项目的所有接口信息（ID和名称）

    run:
        运行项目
    """
    queryset = Projects.objects.all()
    serializer_class = ProjectsModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        results = response.data['results']
        data_list = []
        for item in results:
            project_id = item.get('id')
            interface_testcase_qs = Interfaces.objects.values('id').annotate(testcases=Count('testcases')). \
                filter(project_id=project_id)

            # 获取项目下的接口总数
            interfaces_count = interface_testcase_qs.count()

            # 定义初始用例总数为0
            testcases_count = 0
            for one_dict in interface_testcase_qs:
                testcases_count += one_dict.get('testcases')

            # 获取项目下的配置总数
            interface_configure_qs = Interfaces.objects.values('id').annotate(configures=Count('configures')). \
                filter(project_id=project_id)
            configures_count = 0
            for one_dict in interface_configure_qs:
                configures_count += one_dict.get('configures')

            # 获取项目下套件总数
            testsuites_count = Testsuits.objects.filter(project_id=project_id).count()

            item['interfaces'] = interfaces_count
            item['testcases'] = testcases_count
            item['testsuits'] = testsuites_count
            item['configures'] = configures_count
            data_list.append(item)

        response.data['results'] = data_list

        return response

    # 使用action装饰器自定义动作方法
    @action(methods=['get'], detail=False)
    def names(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def interfaces(self, request, *args, **kwargs):
        response = self.retrieve(request, *args, **kwargs)
        response.data = response.data['interfaces']
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

        interface_qs = Interfaces.objects.filter(project=instance)
        if not interface_qs.exists():
            data = {
                'ret': False,
                'msg': '此项目下无接口，无法运行'
            }
            return Response(data, status=400)

        # 定义可运行的用例列表
        runnable_testcase_obj = []
        for interface_obj in interface_qs:
            # 当前项目-接口，用例所在查询集对象
            testcase_qs = Testcases.objects.filter(interface=interface_obj)
            if testcase_qs.exists():
                # 将两个列表合并
                runnable_testcase_obj.extend(list(testcase_qs))

        if len(runnable_testcase_obj) == 0:
            data = {
                'ret': False,
                'msg': '此项目下无用例，无法运行'
            }
            return Response(data, status=400)

        for testcase_obj in runnable_testcase_obj:
            # 生成yaml用例文件
            common.generate_testcase_file(testcase_obj, env, testcase_dir_path)

        # 运行用例（生成报告）
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        if self.action == 'names':
            return ProjectsNamesModelSerializer
        elif self.action == 'interfaces':
            return InterfacesByProjectIdModelSerializer
        elif self.action == 'run':
            return ProjectsRunSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        if self.action == 'run':
            pass
        else:
            serializer.save()
