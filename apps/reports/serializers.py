import re

from rest_framework import serializers
from rest_framework import validators

from .models import Reports
from utils.common import datetime_fmt


class ReportsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        exclude = ('update_time',)

        extra_kwargs = {
            'create_time': {
                'format': datetime_fmt()
            },
            'html': {
                'write_only': True
            }
        }
