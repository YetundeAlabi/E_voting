import csv
import jwt
from datetime import datetime


from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from rest_framework import generics
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from . import serializers
from .serializers import (
    UserSerializer, 
    PollSerializer, 
    CandidateSerializer, 
    UserLoginSerializer, 
    EmailVerificationSerializer 
)
from accounts.models import User
from .utils import Util
from e_voting.models import Candidate, Poll, Vote
from e_voting_api.permissions import IsAdminOrReadOnly



class UserSignUpView(CreateAPIView):
    """Create a new user in the system"""
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            user_data = serializer.data

            token = RefreshToken.for_user(user)
            refresh = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            current_site = get_current_site(request).domain
            relative_link = reverse("email-verify")

            absurl = f'http://{current_site}{relative_link}?token={refresh["access"]}'
            email_body = f'Hi {user.first_name} Use the link below to verify your email \n{absurl}'
            data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify your email"}
            Util.send_email(data)
            
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmail(GenericAPIView):
    """ An endpoint to verify if user email is authentic before login"""
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
        except jwt.ExpiredSigntureError as identifier:
            return Response({"error": 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
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


class PollListView(generics.ListCreateAPIView):
    serializer_class = serializers.PollSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Poll.objects.all()


class PollDetailView(generics.RetrieveUpdateAPIView):
    queryset = Poll.objects.all()
    serializer_class = serializers.PollDetailSerializer
    permission_classes = [IsAdminOrReadOnly]


    def put(self, request, *args, **kwargs):
        poll = self.get_object()  
        serializer = self.get_serializer(poll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# class PollUpdateView(APIView):
#     serializer_class = serializers.PollDetailSerializer

#     def put(self, request, pk):
#         poll = Poll.objects.get()
        
#         data = request.data
#         if poll.start_time < datetime.now().time():
#             raise "Poll has already started."
#         poll.description = data.get("description")
#         poll.start_time = data.get("start_time")
#         poll.end_time = data.get("end_time")
#         poll.name = data.get("name")
#         # if poll.

#         # if poll.is_active:
#         #     return Response({'message': 'Poll is active'}, status=status.HTTP_400_BAD_REQUEST)

#         now = timezone.now().time()
#         if now < poll.start_time:
#             poll.start_time = poll.updated_start_time
#         if now > poll.end_time:
#             poll.end_time = poll.updated_end_time
#         poll.save()

#         serializer = PollSerializer(poll)
#         return Response(serializer.data, status=status.HTTP_200_OK)






class CandidateListView(generics.ListCreateAPIView):
    serializer_class =  CandidateSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        #filter candidates using poll id
        queryset = Candidate.objects.filter(poll_id = self.kwargs["pk"])
        return queryset










# class CandidateImportView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         file_obj = request.data['file']
#         if not file_obj.name.endswith('.csv'):
#             return Response({'error': 'File type not supported'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             decoded_file = file_obj.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
#             serializer = CandidateSerializer(data=reader, many=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






    # def get_serializer_context(self):
    #     poll_id = self.kwargs.get('poll_id')
    #     return {'poll_id': poll_id}

    # def perform_create(self, serializer):
    #     poll_id = self.kwargs.get('poll_id')
    #     poll = Poll.objects.get(id=poll_id)
    #     serializer.save(poll=poll)
    

class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # permission_classes = []