from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('create/', views.group_create, name='create'),
    path('<int:pk>/', views.group_detail, name='detail'),
    path('<int:pk>/edit/', views.group_edit, name='edit'),
    path('<int:pk>/delete/', views.group_delete, name='delete'),
    path('<int:pk>/invite/', views.invite_member, name='invite'),
    path('<int:pk>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('invitation/<int:pk>/accept/', views.accept_invitation, name='accept_invitation'),
    path('<int:pk>/archive/', views.group_archive, name='archive'),
    path('<int:pk>/export/', views.export_group_csv, name='export_csv'),
]
