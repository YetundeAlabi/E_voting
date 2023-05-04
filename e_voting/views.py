from django.shortcuts import render
from verify_email.email_handler import send_verification_email
# Create your views here.
from django.views.generic import TemplateView
from verify_email.views import VerifyEmailView


class SignUpView(TemplateView):
    template_name = 'signup.html'

class VerifyEmail(VerifyEmailView):
    template_name = 'verify_email.html'
    success_url = '/email-verified/'

# urlpatterns = [
#     path('', SignUpView.as_view(), name='signup'),
#     path('verify-email/', VerifyEmail.as_view(), name='verify_email'),
#     # ...
# ]

