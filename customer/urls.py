from django.urls import path
from .views import (
    CustomerListCreateView, CustomerDetailView, CustomerPolicyListView,
    NomineeListCreateView, NomineeDetailView,
    PaymentListCreateView, PaymentDetailView,AssignPolicyListCreateView,AssignPolicyRetrieveUpdateDestroyView,FamilyMemberListCreateView,FamilyMembweRetrieveUpdateDestroyAPIView,CustomerPolicyCountView,CompanyTotalPolicyListView,GeneralCategoryPolicySalesView,AgentIncentiveListView,AgentIncentiveDetailView,UserIncentiveListView
)

urlpatterns = [
    # Customer URLs
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:customer_id>/policies/', CustomerPolicyListView.as_view(), name='customer-policies'),

    #family_members URLs
    path('members/',FamilyMemberListCreateView.as_view(), name="family_members-list-create"),
    path('members/<int:pk>/',FamilyMembweRetrieveUpdateDestroyAPIView.as_view(), name="family_memebrs-retrieve-update-destroy"),

    #policy URLs
    path('policy/',AssignPolicyListCreateView.as_view(),name='policy-customer-create'),
    path('policy/<int:pk>/',AssignPolicyRetrieveUpdateDestroyView.as_view(),name="policy-customer-retrieve-update-destroy"),

    # Nominee URLs
    path('nominees/', NomineeListCreateView.as_view(), name='nominee-list-create'),
    path('nominees/<int:pk>/', NomineeDetailView.as_view(), name='nominee-detail'),

    # Payment URLs
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('policy-count/', CustomerPolicyCountView.as_view(), name='customer-policy-count'),
    path('company/total-policies/', CompanyTotalPolicyListView.as_view(), name='company-total-policies'),
    path('customer/<int:policy_category_id>/policies/', GeneralCategoryPolicySalesView.as_view(), name='customer-policy-by-category'),
    path('agent-incentives/', AgentIncentiveListView.as_view(), name='agent-incentive-list'),
    path('agent-incentives/<int:pk>/', AgentIncentiveDetailView.as_view(), name='agent-incentive-detail'),
    path('user-incentive/',UserIncentiveListView.as_view(),name='user-incentive-list')


]
