from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.response import Response

from .models import DebugTalks
from .serializers import DebugTalksSerializer


class DebugTalksViewSet(mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    """
    list:
        返回debugtalk列表数据

    update:
        全部更新debugtalk

    partial_update:
        部分更新debugtalk

    retrieve:
        获取debugtalk详情数据
    """
    queryset = DebugTalks.objects.all()
    serializer_class = DebugTalksSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ('id', 'project_id')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data_dict = {
            "id": instance.id,
            "debugtalk": instance.debugtalk
        }
        return Response(data_dict)
