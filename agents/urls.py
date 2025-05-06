from django.urls import path
from .views import AgentListCreateAPIView, AgentRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('agent/', AgentListCreateAPIView.as_view(), name="agent-list-create"),
    path('agent/<int:pk>/', AgentRetrieveUpdateDestroyAPIView.as_view(), name="agent-retrieve-update-destroy"),
    # path('agent-commissions/', AgentCommissionListCreateAPIView.as_view(), name='agent-commissions'),
    # path('agent-commissions/<int:pk>/', AgentCommissionRetrieveUpdateDestroyAPIView.as_view(), name='agent-commission-retrieve-update-destroy'),
]
