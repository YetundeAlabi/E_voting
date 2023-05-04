from rest_framework import generics
from .serializers import UserSerializer, PollSerializer, CandidateSerializer
from accounts.models import User
from rest_framework import status, serializers,permissions

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreatePollView(generics.CreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]


class CreateCandidateView(generics.CreateAPIView):
    serializer_class =  CandidateSerializer
    permission_classes = [permissions.IsAdminUser]
    

class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]