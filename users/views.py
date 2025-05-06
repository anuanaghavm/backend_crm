from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,generics
from .models import User
from .serializers import UserSerializer
from login.views import IsAdmin,IsAdminOrBranchManager,IsUser
from login.serializers import RegisterSerializer
from .models import User, Role


class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrBranchManager]  # Require JWT Authentication

    def get(self, request):
        # Retrieve all user instances
        users = User.objects.all()

        # Serialize the user data
        user_serializer = UserSerializer(users, many=True)

        # Format the created_date field to only show the date (no time)
        for user in user_serializer.data:
            # Format created_date as dd-mm-yyyy
            if "created_date" in user:
                user["created_date"] = user["created_date"].split("T")[0]  # Extract date part (before 'T')

        return Response({
            "users": user_serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        account_serializer = RegisterSerializer(data=request.data)
        if account_serializer.is_valid():
            # Save the account (this creates the `Account` instance)
            account = account_serializer.save()

            # Extract role from request data
            role = request.data.get("role")

            # Create the `User` instance
            user_data = {
                "account": account.id,
                "email": request.data.get("email"),
                "name": request.data.get("name"),
                "contact": request.data.get("contact"),
                "address": request.data.get("address"),
                "role": role,
                "branch": request.data.get("branch"),
                "target": request.data.get("target"),
                "job_type": request.data.get("job_type"),
                "created_by": request.user.id , # Assuming `created_by` is the logged-in user's account ID
                
            }

            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save()

                # Format the created_date field to only show the date (no time)
                created_date = user.created_date
                formatted_date = created_date.strftime("%d-%m-%Y")  # Format to the desired format

                # Generate a role-specific success message
                if role == "2":  # Assuming role is sent as a string
                    message = "Branch Manager created successfully"
                elif role == "3":  # Assuming role is sent as a string
                    message = "User created successfully"
                else:
                    message = "User created successfully"  # Default message for other roles

                # Return response with formatted created_date
                response_data = user_serializer.data
                response_data["created_date"] = formatted_date  # Replace with formatted date

                return Response({
                    "message": message,
                    "user_data": response_data
                }, status=status.HTTP_201_CREATED)
            else:
                account.delete()  # Cleanup the account if user creation fails
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated,IsAdminOrBranchManager]  # Require JWT Authentication

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
class UsersByRoleView(APIView):
    def get(self, request, role_id):
        try:
            # Fetch the role
            role = Role.objects.get(id=role_id)

            # Filter users by the role
            users = User.objects.filter(role=role)

            # Serialize the data
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
