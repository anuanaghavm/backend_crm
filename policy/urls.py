from django.urls import path
from .views import (
    CompanyListCreateAPIView, CompanyRetrieveUpdateDestroyAPIView,
    PolicyCategoryListCreateAPIView, PolicyCategoryRetrieveUpdateDestroyAPIView,
    PolicyListCreateAPIView, PolicyRetrieveUpdateDestroyAPIView,PolicyDetailAPIView,policytypeListCreateAPIView,policytypeRetrieveUpdateDestroyAPIView,CompanyPolicyListView,PlanListCreateAPIView,PlanRetrieveUpateDestroyAPIView,PlanCoverageListCreateAPIView,PlanCoverageRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('companies/', CompanyListCreateAPIView.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', CompanyRetrieveUpdateDestroyAPIView.as_view(), name='company-retrieve-update-destroy'),
    path('policy-categories/', PolicyCategoryListCreateAPIView.as_view(), name='policy-category-list-create'),
    path('policy-categories/<int:pk>/', PolicyCategoryRetrieveUpdateDestroyAPIView.as_view(), name='policy-category-retrieve-update-destroy'),
    path('policy_type/', policytypeListCreateAPIView.as_view(), name='policy-list-create'),
    path('policy_type/<int:pk>/', policytypeRetrieveUpdateDestroyAPIView.as_view(), name='policy-retrieve-update-destroy'),
    path('policies/', PolicyListCreateAPIView.as_view(), name='policy-list-create'),
    path('policies/<int:pk>/', PolicyRetrieveUpdateDestroyAPIView.as_view(), name='policy-retrieve-update-destroy'),
    path('policies/detail/<int:pk>/', PolicyDetailAPIView.as_view(), name='policy-detail'),  # New detailed policy API
    path('company/<int:company_id>/policies/', CompanyPolicyListView.as_view(), name='company-policy-list'),
    path('plan/',PlanListCreateAPIView.as_view(), name="plan-list-create"),
    path('plan/<int:pk>/',PlanRetrieveUpateDestroyAPIView.as_view(),name= "plan-retrieve-update-destroy"),
    path('plan-coverage/',PlanCoverageListCreateAPIView.as_view(),name="plan-coverage-list-create"),
    path('path-coverage/<int:pk>/',PlanCoverageRetrieveUpdateDestroyAPIView.as_view(),name="plan-coverage-retrieve-update-destroy")

]
