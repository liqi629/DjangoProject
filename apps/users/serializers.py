from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from rest_framework_jwt.utils import api_settings


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(label='确认密码', help_text='确认密码', write_only=True,
                                             min_length=6, max_length=20,
                                             error_messages={
                                                 'min_length': '只能输入6-20个字符的密码',
                                                 'max_length': '只能输入6-20个字符的密码'}
                                             )
    token = serializers.CharField(label='生成的token', help_text='生成的token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'token', 'password_confirm')

        extra_kwargs = {
            'username': {
                'label': '用户名',
                'help_text': '用户名',
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '只能输入6-20个字符的用户名',
                    'max_length': '只能输入6-20个字符的用户名'
                }
            },
            'email': {
                'label': '邮箱',
                'help_text': '邮箱',
                'write_only': True,
                'required': True,
                'validators': [UniqueValidator(queryset=User.objects.all(), message="此邮箱已注册")]
            },
            'password': {
                'label': '密码',
                'help_text': '密码',
                'write_only': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '只能输入6-20个字符的密码',
                    'max_length': '只能输入6-20个字符的密码'
                }
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError("密码输入不一致！")
        return attrs

    def create(self, validated_data):
        # 删除User模型中没有的字段
        validated_data.pop('password_confirm')
        # 对密码加密
        user = User.objects.create_user(**validated_data)
        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user
