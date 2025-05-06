from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, Nominee, Payment,CustomerPolicy,FamilyMember,AgentIncentive,UserIncentive
from .serializers import CustomerSerializer, NomineeSerializer, PaymentSerializer,PolicyCustomerSerializer,FamilyMemberSerializer,AgentIncentiveSerializer,UserIncentiveSerializer
from policy.models import Policy
from policy.serializers import PolicySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import CustomerPolicy
from agents.models import Agent


# Customer Views
class CustomerListCreateView(generics.ListCreateAPIView):
    """
    View to list all customers or create a new customer.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def perform_create(self, serializer):
        """
        Override perform_create to associate the customer with the authenticated user.
        """
        user = self.request.user  # The user from the JWT token
        serializer.save(created_by=user)

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated] 

class FamilyMemberListCreateView(generics.ListCreateAPIView):
    """
    View to list all family members or add a new family member for a customer.
    """
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [IsAuthenticated]

class FamilyMembweRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [IsAuthenticated]

class CustomerPolicyListView(APIView):
    """
    View to list all policies linked to a specific customer.
    """
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
            policies = customer.policies.all()
            serializer = PolicySerializer(policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


# Nominee Views
class NomineeListCreateView(generics.ListCreateAPIView):
    """
    View to list all nominees or create a new nominee for a customer.
    """
    queryset = Nominee.objects.all()
    serializer_class = NomineeSerializer


class NomineeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a nominee.
    """
    queryset = Nominee.objects.all()
    serializer_class = NomineeSerializer


# Payment Views
class PaymentListCreateView(generics.ListCreateAPIView):
    """
    View to list all payments or create a new payment.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a payment.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class AssignPolicyListCreateView(generics.ListCreateAPIView):
    queryset = CustomerPolicy.objects.all()
    serializer_class = PolicyCustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)


class AssignPolicyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific customer-policy assignment.
    """
    queryset = CustomerPolicy.objects.all()
    serializer_class = PolicyCustomerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        try:
            policy = CustomerPolicy.objects.get(pk=pk)
            serializer = PolicyCustomerSerializer(policy)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerPolicy.DoesNotExist:
            return Response({"error": "CustomerPolicy not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk, *args, **kwargs):
        try:
            policy = CustomerPolicy.objects.get(pk=pk)
        except CustomerPolicy.DoesNotExist:
            return Response({"error": "CustomerPolicy not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        allowed_fields = ['coverage_amount1', 'premium_amount1', 'start_date']

        # Exclude 'policy' if it's not explicitly provided
        if 'policy' not in data:
            data['policy'] = policy.policy  # Keep the existing policy

        # Remove fields that are not allowed
        for field in list(data.keys()):
            if field not in allowed_fields:
                data.pop(field)

        serializer = PolicyCustomerSerializer(policy, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, *args, **kwargs):
        try:
            policy = CustomerPolicy.objects.get(pk=pk)
            policy.delete()
            return Response({"message": "CustomerPolicy deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except CustomerPolicy.DoesNotExist:
            return Response({"error": "CustomerPolicy not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomerPolicyCountView(APIView):
    """
    Get the total count of all customer policies.
    """
    def get(self, request, *args, **kwargs):
        # Get the total count of customer policies
        total_policy_count = CustomerPolicy.objects.count()

        return Response({
            'total_customer_policy_count': total_policy_count
        }, status=status.HTTP_200_OK)



class CompanyTotalPolicyListView(APIView):
    """
    View to get the total count of all assigned policies and list all assigned policies.
    """
    def get(self, request, *args, **kwargs):
        # Get the total count of assigned policies
        total_policies_sold = CustomerPolicy.objects.count()
        
        # Get all assigned policies
        policies = CustomerPolicy.objects.all()
        serializer = PolicyCustomerSerializer(policies, many=True)

        return Response({
            "total_policies_sold": total_policies_sold,
            "policies": serializer.data  # List of all assigned policies
        }, status=status.HTTP_200_OK)


class GeneralCategoryPolicySalesView(APIView):
    def get(self, request, policy_category_id):
        try:
            policies = Policy.objects.filter(policy_category_id=policy_category_id)
            
            # Assuming there's a sales field or related model, modify accordingly
            data = [
                {
                    "policy_name": policy.policy_name,
                    "policy_code": policy.policy_code,
                    "category": policy.policy_category.policy_name,  # Adjust field name
                    "premium_amount": policy.premium_amount,
                    "total_sales": policy.sales.count() if hasattr(policy, 'sales') else 0  # Adjust if sales exist
                }
                for policy in policies
            ]

            return Response({"policy_sales": data}, status=200)
        
        except Policy.DoesNotExist:
            return Response({"error": "No policies found for this category."}, status=404)

# List and Create Agent Incentives
class AgentIncentiveListView(generics.ListAPIView):
    queryset = AgentIncentive.objects.all()
    serializer_class = AgentIncentiveSerializer
    http_method_names = ['get']  # Only allow GET method

# View to retrieve, update (patch), and delete a specific agent incentive
class AgentIncentiveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AgentIncentive.objects.all()
    serializer_class = AgentIncentiveSerializer
    http_method_names = ['get', 'patch', 'delete']

class UserIncentiveListView(APIView):
    def get(self, request):
        incentives = UserIncentive.objects.all()  # Fetch all incentives
        serializer = UserIncentiveSerializer(incentives, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)