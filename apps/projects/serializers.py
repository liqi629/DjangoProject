from rest_framework import serializers

from debugtalks.models import DebugTalks
from projects.models import Projects
from interfaces.models import Interfaces
from utils import common, validates


class ProjectsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        exclude = ('update_time',)

        extra_kwargs = {
            'create_time': {
                'read_only': True,
                'format': common.datetime_fmt(),
            },
        }

    def create(self, validated_data):
        # 在创建项目时，同时创建一个空的debugtalk.py文件
        project = super().create(validated_data)
        DebugTalks.objects.create(project=project)
        return project


class ProjectsNamesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ('id', 'name')


class InterfacesNamesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interfaces
        fields = ('id', 'name')


class InterfacesByProjectIdModelSerializer(serializers.ModelSerializer):
    interfaces = InterfacesNamesModelSerializer(many=True, read_only=True)

    class Meta:
        model = Projects
        fields = ('interfaces',)


class ProjectsRunSerializer(serializers.ModelSerializer):
    env_id = serializers.IntegerField(label='环境变量ID', help_text='环境变量ID',
                                      write_only=True, validators=[validates.is_exised_env_id])

    class Meta:
        model = Projects
        fields = ('id', 'env_id')
