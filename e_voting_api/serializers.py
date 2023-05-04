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


class CandidateDetailSerializer(serializers.ModelField):
    poll = PollSerializer(many=True, read_only=True)

    model = Candidate
    fields = ["id", "name", "poll"]


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        field = "__all__"
