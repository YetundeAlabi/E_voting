from datetime import datetime

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from e_voting.models import Candidate, Vote, Poll, Voter
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")

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
        fields = ["name", "description"]


class PollDetailSerializer(serializers.ModelSerializer):
    candidates = serializers.StringRelatedField(many=True, read_only=True, required=False)

    class Meta:
        model = Poll
        fields = "__all__"

    def update(self, instance, validated_data):

        """update start and end time before a poll start """
        if instance.start_time > datetime.now().time() and instance.end_time > datetime.now().time(): #update poll when it has not started
            instance.start_time = validated_data.get("start_time", instance.start_time)
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("description", instance.name)
            # instance.save()  

            """extend end time of poll when a poll is active"""
        elif instance.start_time < datetime.now().time() < instance.end_time: #extend end time of poll when a poll is active
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("name", instance.name)
            
            """ can't update a poll start_time when poll is active or update end time when poll has ended """
        elif instance.end_time < datetime.now().time() or instance.start_time < datetime.now().time():
            raise serializers.ValidationError("Poll has already started or ended.")
        
        return instance



# class CandidateSerializer(serializers.ModelSerializer):
#     poll = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Poll.objects.all())

#     class Meta:
#         model = Candidate
#         fields = ["name", "poll"]

class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        # fields = ['id', 'poll', 'candidate', 'voted_by']
        fields = "__all__"


class CandidateSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, required=False)

    class Meta:
        model = Candidate
        fields = "__all__"

    # def create(self, validated_data):
    #     poll_id = self.context.get("poll_id")
    #     validated_data["poll_id"] = poll_id
    #     return super().create(validated_data)


class CandidateDetailSerializer(serializers.ModelSerializer):
    poll = PollSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = ["id", "name", "poll"]


class VotersPollSerializer(serializers.ModelSerializer):
    polls = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id"]

    def get_polls(self, obj):
        # polls = obj.
        pass



class VoterImportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = "__all__"
