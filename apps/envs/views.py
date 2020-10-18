from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Envs
from .serializers import EnvsModelSerializer, EnvsNamesSerializer


class EnvsViewSet(ModelViewSet):
    """
        create:
            创建环境变量

        retrieve:
            获取环境变量详情数据

        update:
            完整更新环境变量

        partial_update:
            部分更新环境变量

        destroy:
            删除环境变量

        list:
            获取环境变量列表数据

        names:
            返回所有环境变量ID和名称
    """
    queryset = Envs.objects.all()
    serializer_class = EnvsModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id', 'name']

    @action(detail=False)
    def names(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        return EnvsNamesSerializer if self.action == 'names' else self.serializer_class
