from django.shortcuts import render,get_object_or_404
from rest_framework import generics,permissions
from .models import Company, PolicyCategory, Policy,PolicyType,Plan,PlanCoverage
from rest_framework.permissions import IsAuthenticated
from .serializers import CompanySerializer, PolicyCategorySerializer, PolicySerializer,PolicyTypeSerializer,PlanSerializer,PlanCoverageSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Policy, Company
from rest_framework.response import Response
from .serializers import PolicySerializer
from rest_framework import serializers



class CompanyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class CompanyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class policytypeListCreateAPIView(generics.ListCreateAPIView):
    queryset =PolicyType .objects.all()
    serializer_class = PolicyTypeSerializer
    permission_classes = [IsAuthenticated]


class policytypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PolicyType.objects.all()
    serializer_class = PolicyTypeSerializer
    permission_classes = [IsAuthenticated]


class PolicyCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = PolicyCategory.objects.all()
    serializer_class = PolicyCategorySerializer
    permission_classes = [IsAuthenticated]

class PolicyCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PolicyCategory.objects.all()
    serializer_class = PolicyCategorySerializer
    permission_classes = [IsAuthenticated]


class PolicyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated]


class PolicyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated]



# New view for fetching detailed policy information
class PolicyDetailAPIView(generics.RetrieveAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated]

class CompanyPolicyListView(generics.ListAPIView):
    serializer_class = PolicySerializer
    permission_classes = [IsAuthenticated]  # Add authentication if needed

    def get_queryset(self):
        """
        Filter policies based on the company.
        """
        company_id = self.kwargs.get('company_id')  # Get company ID from URL
        return Policy.objects.filter(company_id=company_id)
    
    def list(self, request, *args, **kwargs):
        """
        Customize the response format.
        """
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No policies found for this company"}, status=404)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

class PlanListCreateAPIView(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

class PlanRetrieveUpateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

class PlanCoverageListCreateAPIView(generics.ListCreateAPIView):
    queryset = PlanCoverage.objects.all()
    serializer_class = PlanCoverageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        plan = self.request.data.get('plan')  # Ensure this is provided in request
        if not plan:
            raise serializers.ValidationError({"plan": "This field is required."})
        plan = get_object_or_404(Plan, id=plan)
        serializer.save(plan=plan)

class PlanCoverageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlanCoverage.objects.all()
    serializer_class = PlanCoverageSerializer
    permission_classes = [IsAuthenticated]