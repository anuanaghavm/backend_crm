from django.urls import path
from .views import AadhaarVerificationView,PanCardVerificationView,BankVerificationView,UPIVerificationView

urlpatterns = [
    path('aadhaar-validate/', AadhaarVerificationView.as_view(), name='aadhaar-validation'),  # Add .as_view()
    path('pan-validate/', PanCardVerificationView.as_view(), name='pan-validation'),
    path("bank-verification/", BankVerificationView.as_view(), name="bank_verification"),
    path("upi-verification/", UPIVerificationView.as_view(), name="upi-verification"),


]
