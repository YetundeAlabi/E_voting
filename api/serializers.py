from datetime import datetime

from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Candidate, Vote, Poll, Voter
from accounts.serializers import UserDetailSerializer

User = get_user_model()


class PollListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        fields = ["id", "name", "description", "start_time", "end_time"]

        
class PollSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if instance.is_active:
            serializer_class = PollDetailSerializer
        else:
            serializer_class = PollResultSerializer

        serializer = serializer_class(instance, context=self.context)
        return serializer.data



class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        fields = "__all__"


class VoterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = "__all__"
        read_only_fields = ['id']

    def create(self, validated_data):
        poll_data = validated_data.pop('poll')
        voter = Voter.objects.create(**validated_data, poll=poll_data)
        return voter


class VoterImportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = ['email', 'first_name', "last_name", 'phone_number']
        

    def create(self, validated_data):
        poll_data = validated_data.pop('poll')
        voter = Voter.objects.create(**validated_data, poll=poll_data)
        return voter
    

class PollDetailSerializer(serializers.ModelSerializer):
    candidates = serializers.StringRelatedField(
        many=True, read_only=True, required=False)
    is_active = serializers.BooleanField()
    # voters = VoterSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ["id", "name", "description", "end_time",
                  "start_time", "candidates", "is_active"]

    def get_is_active(self, obj):
        return obj.is_active()

    
        

    def update(self, instance, validated_data):
        """update start and end time before a poll start """
        if not instance.is_active:  # update poll when it has not started
            instance.start_time = validated_data.get(
                "start_time", instance.start_time)
            instance.end_time = validated_data.get(
                "end_time", instance.end_time)
            instance.description = validated_data.get(
                "description", instance.description)
            instance.name = validated_data.get("description", instance.name)
            instance.save()

            """extend end time of poll when a poll is active"""
        elif instance.is_active:  # extend end time of poll when a poll is active
            instance.end_time = validated_data.get(
                "end_time", instance.end_time)
            instance.description = validated_data.get(
                "description", instance.description)
            instance.name = validated_data.get("name", instance.name)
            instance.save()

            """ can't update a poll start_time when poll is active or update end time when poll has ended """
        elif instance.end_time < datetime.now().time() or instance.start_time < datetime.now().time():
            raise serializers.ValidationError(
                "Poll has already started or ended.")

        return instance


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'poll']
        read_only_fields = ['id']

    

class VoterDetailSerializer(serializers.ModelSerializer):
    poll = PollDetailSerializer()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Voter
        fields = ["id", "email", "full_name", "phone_number", "poll"]

    # def get_poll(self, obj):
    #     polls = obj.poll.filter(id=self.request.user.id).all()
    #     return PollSerializer(polls, many=True).data

    def get_full_name(self, obj):
        return obj.get_full_name()


class FileImportSerializer(serializers.Serializer):
    file = serializers.FileField(
        max_length=200, allow_empty_file=False, use_url=False)

    def validate(self, data):
        file = data.get("file", None)
        if not file:
            raise serializers.ValidationError('Please provide a file.')

        """ Check that the file uploaded is csv file"""
        if not file.name.endswith(".csv"):
            raise serializers.ValidationError(
                "File type not supported. file must be a csv file")
        return data

    def create(self, validated_data):
        file = validated_data['file']
        return file


class CandidateDetailSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Candidate
        fields = ["name", "vote_count"]

    def get_vote_count(self, obj):
        return obj.get_vote_count()


class PollResultSerializer(PollDetailSerializer):
    total_votes = serializers.SerializerMethodField(read_only=True)
    candidates = CandidateDetailSerializer(many=True, read_only=True)
    winner = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ["id", "name", "description", "end_time", "start_time",
                  "candidates", "is_active", "voter", "winner", "total_votes"]

    def get_total_votes(self, obj):
        return obj.get_total_vote()

    def get_winner(self, obj):
        """get all candidates votes and arrange by descending order. winner is the first candidate"""
        queryset = obj.candidates.annotate(vote_count=Count(
            "candidate_votes")).order_by('-vote_count')
        if queryset.exists():
            winner = queryset[0]
            serializer = CandidateDetailSerializer(winner)
            return serializer.data


class PollWinnerSerializer(serializers.ModelSerializer):
    poll_name = serializers.CharField(source='poll.name')
    winner_name = serializers.CharField(source='candidate.name')

    class Meta:
        model = Vote
        fields = ('poll_name', 'winner_name')

class PollSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if instance.is_active:
            serializer_class = PollDetailSerializer
        else:
            serializer_class = PollResultSerializer

        serializer = serializer_class(instance, context=self.context)
        return serializer.data





