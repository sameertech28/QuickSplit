from django.urls import path
from . import views

app_name = 'settlements'

urlpatterns = [
    path('group/<int:group_id>/', views.settlement_list, name='list'),
    path('group/<int:group_id>/record/', views.settlement_create, name='create'),
    path('<int:pk>/complete/', views.settlement_complete, name='complete'),
]
