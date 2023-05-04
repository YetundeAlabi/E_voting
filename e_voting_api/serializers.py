from django.contrib.auth import get_user_model
from rest_framework import serializers
from e_voting.models import Candidate, Vote, Poll 


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the voters object"""

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name",
                  "last_name", "phone_number"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """ create a new user """
        return User.objects.create_user(**validated_data)
    

class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        field = ["name", "poll"]

class PollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        field = "__all__"