from django.db.models import Sum
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Projects
from interfaces.models import Interfaces
from testsuits.models import Testsuits
from testcases.models import Testcases
from configures.models import Configures
from envs.models import Envs
from debugtalks.models import DebugTalks
from reports.models import Reports


class SummaryViewSet(APIView):
    def get(self, request, *args, **kwargs):
        data = {}
        # 组装user信息
        user = request.user
        data['user'] = {
            "username": user.username,
            "role": "管理员" if user.is_superuser == 1 else "普通用户",
            "date_joined": user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S')
        }
        # 组装statistic信息
        projects_count = Projects.objects.all().count()
        interfaces_count = Interfaces.objects.all().count()
        testcases_count = Testcases.objects.all().count()
        testsuits_count = Testsuits.objects.all().count()
        configures_count = Configures.objects.all().count()
        envs_count = Envs.objects.all().count()
        debug_talks_count = DebugTalks.objects.all().count()
        reports_count = Reports.objects.all().count()
        # 获取总的执行用例数
        total = Reports.objects.all().aggregate(total=Sum('count')).get('total')
        # 获取总的执行成功用例数
        success = Reports.objects.all().aggregate(success=Sum('success')).get('success')
        # 计算成功率  round(success/float(total), 2) 浮点数计算保留两位小数
        success_rate = int(round(success / float(total), 2) * 100)
        fail_rate = 100 - success_rate

        data['statistics'] = {
            "projects_count": projects_count,
            "interfaces_count": interfaces_count,
            "testcases_count": testcases_count,
            "testsuits_count": testsuits_count,
            "configures_count": configures_count,
            "envs_count": envs_count,
            "debug_talks_count": debug_talks_count,
            "reports_count": reports_count,
            "success_rate": success_rate,
            "fail_rate": fail_rate
        }
        request.user.last_login = str(datetime.today())
        request.user.save()
        return Response(data)
