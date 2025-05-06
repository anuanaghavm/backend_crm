from django.http import JsonResponse
from django.views import View
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.conf import settings
import json

@method_decorator(csrf_exempt, name='dispatch')  # ✅ Disable CSRF for this view
class AadhaarVerificationView(View):
    def get(self, request):
        return JsonResponse({"message": "Use POST method with Aadhaar number"}, status=405)

    def post(self, request):
        try:
            data = json.loads(request.body)  # ✅ Parse JSON body correctly
            aadhaar_number = data.get('aadhaar_number')  # ✅ Extract Aadhaar number
            
            if not aadhaar_number:
                return JsonResponse({'error': 'Aadhaar number is required'}, status=400)

            api_url = 'https://kyc-api.surepass.io/api/v1/aadhaar-validation/aadhaar-validation'

            headers = {
                'Authorization': f'Bearer {settings.SUREPASS_API_KEY}',
                'Content-Type': 'application/json',
            }

            payload = json.dumps({'id_number': aadhaar_number})
            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({'error': 'Verification failed', 'details': response.text}, status=response.status_code)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')  # ✅ Disable CSRF for this view
class PanCardVerificationView(View):
    def get(self, request):
        return JsonResponse({"message": "Use POST method with PAN number"}, status=405)

    def post(self, request):
        try:
            data = json.loads(request.body)  # ✅ Parse JSON body correctly
            pan_number = data.get('pan_number')  # ✅ Extract PAN number
            
            if not pan_number:
                return JsonResponse({'error': 'PAN number is required'}, status=400)

            api_url = 'https://kyc-api.surepass.io/api/v1/pan/pan'

            headers = {
                'Authorization': f'Bearer {settings.SUREPASS_API_KEY}',
                'Content-Type': 'application/json',
            }

            payload = json.dumps({'id_number': pan_number})
            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({'error': 'Verification failed', 'details': response.text}, status=response.status_code)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        


@method_decorator(csrf_exempt, name="dispatch")  # ✅ Disable CSRF for this view
class BankVerificationView(View):
    def get(self, request):
        return JsonResponse({"message": "Use POST method with bank details"}, status=405)

    def post(self, request):
        try:
            data = json.loads(request.body)  # ✅ Parse JSON body correctly
            account_number = data.get("account_number")  # ✅ Extract Account Number
            ifsc_code = data.get("ifsc")  # ✅ Extract IFSC Code

            if not account_number or not ifsc_code:
                return JsonResponse({"error": "Account number and IFSC code are required"}, status=400)

            api_url = "https://kyc-api.surepass.io/api/v1/bank-verification/"
            headers = {
                "Authorization": f"Bearer {settings.SUREPASS_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = json.dumps({"id_number": account_number, "ifsc": ifsc_code, "ifsc_details": True})
            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                return JsonResponse(response.json())  # ✅ Return API response
            else:
                return JsonResponse({"error": "Verification failed", "details": response.text}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


@method_decorator(csrf_exempt, name="dispatch")  # ✅ Disable CSRF for this view
class UPIVerificationView(View):
    def get(self, request):
        return JsonResponse({"message": "Use POST method with UPI ID"}, status=405)

    def post(self, request):
        try:
            data = json.loads(request.body)  # ✅ Parse JSON body correctly
            upi_id = data.get("upi_id")  # ✅ Extract UPI ID

            if not upi_id:
                return JsonResponse({"error": "UPI ID is required"}, status=400)

            api_url = "https://kyc-api.surepass.io/api/v1/bank-verification/upi-verification"
            headers = {
                "Authorization": f"Bearer {settings.SUREPASS_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = json.dumps({"upi_id": upi_id})
            response = requests.post(api_url, data=payload, headers=headers)

            if response.status_code == 200:
                return JsonResponse(response.json())  # ✅ Return API response
            else:
                return JsonResponse({"error": "Verification failed", "details": response.text}, status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
