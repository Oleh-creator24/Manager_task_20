from django.urls import path
from .views_tasks import TaskListCreateView, TaskDetailUpdateDeleteView
from .views_subtasks import SubTaskListCreateView, SubTaskDetailUpdateDeleteView
from . import views

urlpatterns = [
    # HTML для списка задач (оставляем для удобства)
    path("", views.task_list_html, name="home"),

    # --- Tasks (Generic Views) ---
    path("api/tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("api/tasks/<int:pk>/", TaskDetailUpdateDeleteView.as_view(), name="task-detail-update-delete"),

    # --- SubTasks (Generic Views) ---
    path("api/subtasks/", SubTaskListCreateView.as_view(), name="subtask-list-create"),
    path("api/subtasks/<int:pk>/", SubTaskDetailUpdateDeleteView.as_view(), name="subtask-detail-update-delete"),

    # --- Stats (оставляем FBV как в задании) ---
    path("api/stats/", views.api_task_stats, name="api_task_stats"),
]
