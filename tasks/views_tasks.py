# tasks/views_tasks.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Task
from .serializers import (
    TaskCreateSerializer,
    TaskDetailSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")
class TaskListCreateView(generics.ListCreateAPIView):
    """
    Список задач + создание новой задачи
    Поддерживает:
    - фильтрацию: ?status_id=1 или ?status__name=To Do
    - поиск: ?search=слово (ищет в title, description)
    - сортировку: ?ordering=created_at или ?ordering=-created_at
    """
    queryset = Task.objects.all().select_related("status")
    serializer_class = TaskCreateSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "status": ["exact"],  # фильтр по id (например ?status=1)
        "status__name": ["exact"],  # фильтр по имени (например ?status__name=To Do)
        "deadline": ["exact", "lte", "gte"],
    }

    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]


@method_decorator(csrf_exempt, name="dispatch")
class TaskDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали задачи + обновление + удаление
    """
    queryset = Task.objects.all().select_related("status")
    serializer_class = TaskDetailSerializer
    permission_classes = [AllowAny]
