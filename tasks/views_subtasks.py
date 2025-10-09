# tasks/views_subtasks.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import SubTask
from .serializers import (
    SubTaskCreateSerializer,
    SubTaskDetailSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")
class SubTaskListCreateView(generics.ListCreateAPIView):
    """
    Список подзадач + создание новой подзадачи
    Поддерживает:
    - фильтрацию: ?status_id=2 или ?status__name=Done
    - поиск: ?search=слово (ищет в title, description)
    - сортировку: ?ordering=created_at или ?ordering=-created_at
    """
    queryset = SubTask.objects.all().select_related("task", "status")
    serializer_class = SubTaskCreateSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status_id", "status__name", "deadline", "task_id"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]


@method_decorator(csrf_exempt, name="dispatch")
class SubTaskDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали подзадачи + обновление + удаление
    """
    queryset = SubTask.objects.all().select_related("task", "status")
    serializer_class = SubTaskDetailSerializer
    permission_classes = [AllowAny]
