from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Branch
from .serializers import BranchSerializer
from rest_framework.response import Response
from users.models import User  

class BranchListCreateView(ListCreateAPIView):
    """
    Handles listing all branches and creating a new branch.
    """
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer  # Specify the serializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        Add extra context to the serializer for including users if required.
        """
        context = super().get_serializer_context()
        context['include_users'] = True  # Include users in the response
        return context

def perform_create(self, serializer):
    """
    Override to handle additional logic during branch creation.
    """
    branch = serializer.save()  # Save the branch instance

    # Assign branch only to users that were pre-linked by their branch ID
    users = User.objects.filter(branch_id=branch.id)  # Filter users with the current branch ID
    for user in users:
        user.branch = branch
        user.save()  # Save the updated user with the branch assigned

class BranchRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a branch.
    """
    queryset = Branch.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return BranchSerializer
