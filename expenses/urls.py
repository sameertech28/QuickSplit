from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('group/<int:group_id>/add/', views.expense_create, name='create'),
    path('<int:pk>/', views.expense_detail, name='detail'),
    path('<int:pk>/edit/', views.expense_edit, name='edit'),
    path('<int:pk>/delete/', views.expense_delete, name='delete'),
    path('<int:expense_id>/contribute/', views.contribution_add, name='contribution_add'),
    path('contribution/<int:pk>/delete/', views.contribution_delete, name='contribution_delete'),
    path('group/<int:group_id>/scan-receipt/', views.scan_receipt, name='scan_receipt'),
]
