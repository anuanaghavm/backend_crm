from django.urls import path
from .views import UserListCreateView,UserDetailView,UsersByRoleView


urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/role/<int:role_id>/', UsersByRoleView.as_view(), name='users-by-role'),

]
