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
        fields = ["id", "name", "description"]


class PollDetailSerializer(serializers.ModelSerializer):
    candidates = serializers.StringRelatedField(many=True, read_only=True, required=False)
    is_active = serializers.BooleanField()

    class Meta:
        model = Poll
        fields = ["id", "name", "description", "candidates", "is_active"]

    def get_is_active(self, obj):
        return obj.is_active()

    def update(self, instance, validated_data):

        """update start and end time before a poll start """
        if not instance.is_active(): #update poll when it has not started
            instance.start_time = validated_data.get("start_time", instance.start_time)
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("description", instance.name)
            instance.save()  

            """extend end time of poll when a poll is active"""
        elif instance.is_active(): #extend end time of poll when a poll is active
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("name", instance.name)
            instance.save()

            """ can't update a poll start_time when poll is active or update end time when poll has ended """
        elif instance.end_time < datetime.now().time() or instance.start_time < datetime.now().time():
            raise serializers.ValidationError("Poll has already started or ended.")
        
        return instance
    

class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "full_name", "phone_number"]

    def get_full_name(self, obj):
        return obj.get_full_name()

class VotersPollSerializer(serializers.ModelSerializer):
    # polls = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ["id"]

    
class UserEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        print(data)
        user = User.objects.get(email=data)
        print(user)
        try:
            user = User.objects.filter(email=data).exists()
            if user:
                return data
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')
        

class VoterSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Voter
        fields = ['id', 'user', 'poll']
        read_only_fields = ['id']


class AddVoterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    poll_id = serializers.IntegerField()

    def create(self, validated_data):
        email = validated_data['email']
        poll_id = validated_data['poll_id']
        user = User.objects.get(email=email)
        poll = Poll.objects.get(id=poll_id)
        if Voter.objects.filter(user=user, poll=poll).exists():
            raise serializers.ValidationError("A voter with the same user and poll already exists.")
        return Voter.objects.create(user=user, poll=poll)
        

class VoterEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User with this email does not exist.'})
        
        poll_id = self.context.get('poll_id')
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise serializers.ValidationError({'poll_id': 'Poll with this id does not exist.'})
        
        if poll.is_active():
            raise serializers.ValidationError("Cannot add voter to an active pol")
        
        if Voter.objects.filter(user=user, poll=poll).exists():
            raise serializers.ValidationError({'error': 'Voter with the same user and poll id already exists.'})
        return Voter.objects.create(user=user, poll=poll)
    
# class VoterSerializer(serializers.ModelSerializer):
   
#     # user = UserDetailSerializer(read_only=True)
#     user = UserEmailField()
#     # poll = PollSerializer()
    

#     class Meta:
#         model = Voter
#         # fields = ["id", "user", "poll"]
#         fields = "__all__"

#     def create(self, validated_data):
#         print(validated_data)
#         # Check if a voter with the same user_id and poll already exists
#         if Voter.objects.filter(user=validated_data['user'], poll=validated_data['poll']).exists():
#             raise serializers.ValidationError("A voter with the same user and poll already exists.")
#         user = validated_data.pop("user")
#         poll = validated_data.pop("poll") 
        
#         return Voter.objects.create(user=user, poll=poll)
        # Create the new voter object
        # return Voter.objects.create(user=self.context['request'].user, poll=poll)

    # def create(self, validated_data):
    #     print(validated_data)
    #     user = self.context["request"].user
    #     poll = validated_data.pop("poll") 
    #     return Voter.objects.create(user=user, poll=poll)

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




class VoterImportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = "__all__"
