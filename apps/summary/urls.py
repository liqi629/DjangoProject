from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.SummaryViewSet.as_view()),
]
