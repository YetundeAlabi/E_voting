from urllib import response
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from .serializers import UserSerializer, PollSerializer, CandidateSerializer, UserLoginSerializer, EmailVerificationSerializer 
from accounts.models import User
from .utils import Util
import jwt


class UserSignUpView(generics.CreateAPIView):
    """Create a new user in the system"""
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            user_data = serializer.data

            token = RefreshToken.for_user(user)
            user_data["token"] = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            current_site = get_current_site(request).domain
            relative_link = reverse("email-verify")

            absurl = f'http://{current_site}{relative_link}?token={user_data["token"]["access"]}'
            email_body = f'Hi {user.first_name} Use the link below to verify your email \n{absurl}'
            data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify your email"}
            Util.send_email(data)
            
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id = payload['user_id'])  
            if not user.is_verified:  
                user.is_verified = True
                user.save()
            return Response({"email": 'Successfully activated'}, status=status.HTTP_200_OK)
        # except jwt.ExpiredSigntureError as identifier:
        #     return Response({"error": 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({"error": 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        
        return Response(data, status=status.HTTP_200_OK)


class CreatePollView(generics.CreateAPIView):
    serializer_class = PollSerializer
    permission_classes = (IsAdminUser)


class CreateCandidateView(generics.CreateAPIView):
    serializer_class =  CandidateSerializer
    permission_classes = [IsAdminUser]
    

class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]