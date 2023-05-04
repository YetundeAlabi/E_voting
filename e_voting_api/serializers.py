from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from e_voting.models import Candidate, Vote, Poll
from rest_framework.exceptions import AuthenticationFailed


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
    

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=500)

    class Meta:
        model = User
        fields = ["token"] 


class UserLoginSerializer(serializers.ModelSerializer):
    """Serializer to authenticate users with email and password"""
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, validated_data):
        user = authenticate(**validated_data)
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials") 


class PollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        field = "__all__"


class CandidateSerializer(serializers.ModelSerializer):
    poll = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Poll.objects.all())

    class Meta:
        model = Candidate
        field = ["name", "poll"]


class CandidateDetailSerializer(serializers.ModelSerializer):
    poll = PollSerializer(many=True, read_only=True)

    model = Candidate
    fields = ["id", "name", "poll"]


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        field = "__all__"
