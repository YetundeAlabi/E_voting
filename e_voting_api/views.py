from rest_framework import generics
from .serializers import UserSerializer
from accounts.models import User
from rest_framework import status, serializers,permissions

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]