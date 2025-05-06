from rest_framework import generics, permissions
from .models import Agent
from .serializers import AgentSerializer
from rest_framework.permissions import IsAuthenticated

class AgentListCreateAPIView(generics.ListCreateAPIView):
    """
    Handles listing and creating agents.
    Returns all agents regardless of the authenticated user's role.
    """
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all agents irrespective of the authenticated user's role
        return Agent.objects.all()

    def perform_create(self, serializer):
        """
        Save the agent with the `created_by` field set to the logged-in user.
        """
        serializer.save(created_by=self.request.user)


class AgentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting an agent.
    Allows access to all agents irrespective of the authenticated user's role.
    """
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Agent.objects.all()

