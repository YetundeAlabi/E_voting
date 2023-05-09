from datetime import datetime

from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Candidate, Vote, Poll, Voter
from accounts.serializers import UserDetailSerializer

User = get_user_model()

class PollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        fields = ["id", "name", "description"]


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        # fields = ['id', 'poll', 'candidate', 'voted_by']
        fields = "__all__"
 

class VoterLoginDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Voter
        fields = ['id', 'user']
        read_only_fields = ['id']


class PollDetailSerializer(serializers.ModelSerializer):
    candidates = serializers.StringRelatedField(many=True, read_only=True, required=False)
    is_active = serializers.BooleanField()
    voter = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ["id", "name", "description", "end_time", "start_time", "candidates", "is_active", "voter"]

    def get_is_active(self, obj):
        return obj.is_active()
    
    def get_voter(self, obj):
        voter = obj.voters.filter(user=self.context['request'].user).first()
        return VoterLoginDetailSerializer(voter).data

    def update(self, instance, validated_data):

        """update start and end time before a poll start """
        if not instance.is_active: #update poll when it has not started
            instance.start_time = validated_data.get("start_time", instance.start_time)
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("description", instance.name)
            instance.save()  

            """extend end time of poll when a poll is active"""
        elif instance.is_active: #extend end time of poll when a poll is active
            instance.end_time = validated_data.get("end_time", instance.end_time)
            instance.description = validated_data.get("description", instance.description)
            instance.name = validated_data.get("name", instance.name)
            instance.save()

            """ can't update a poll start_time when poll is active or update end time when poll has ended """
        elif instance.end_time < datetime.now().time() or instance.start_time < datetime.now().time():
            raise serializers.ValidationError("Poll has already started or ended.")
        
        return instance
    

class CandidateSerializer(serializers.ModelSerializer):
    # votes = VoteSerializer(many=True, required=False)
    name = serializers.CharField()

    class Meta:
        model = Candidate
        fields = ["name"]


class VoterSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Voter
        fields = ['id', 'user', 'poll']
        read_only_fields = ['id']

    
    
class VoterEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User with this email does not exist.'})
        
        poll_id = self.context.get('poll_id')
        poll = self._get_poll(poll_id)
        self._validate_voter(user, poll)
        
        return Voter.objects.create(user=user, poll=poll)
    
    def _get_poll(self, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise serializers.ValidationError({'poll_id': 'Poll with this id does not exist.'})
        return poll
    
    def _validate_voter(self, user, poll):
        if Voter.objects.filter(user=user, poll=poll).exists():
            raise serializers.ValidationError({'error': 'Voter with the same user and poll id already exists.'})
        
        if poll.is_active: #only add a poll before polls begin
            raise serializers.ValidationError("Cannot add voter to an active poll")


class VoterDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    poll = serializers.SerializerMethodField
   
    class Meta:
        model = Voter
        fields = ["id", "user", "poll"]

    def get_poll(self, obj):
        polls = obj.poll.filter(user=self.request.user).all()
        return PollSerializer(polls, many=True).data


class FileImportSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=200, allow_empty_file=False, use_url=False)

    def validate(self, data):
        file = data.get("file", None)
        if not file:
            raise serializers.ValidationError('Please provide a file.')
        
        """ Check that the file uploaded is csv file"""
        if not file.name.endswith(".csv"):
            raise serializers.ValidationError("File type not supported. file must be a csv file")
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

    model=Poll
    fields = ("id", "name", "description", "end_time", "start_time", "candidates", "is_active", "voter", "winner", "total_votes")

    def get_total_votes(self, obj):
        return obj.get_total_vote()
    
    def get_winner(self, obj):
        """get all candidates votes and arrange by descending order. winner is the first candidate"""
        queryset = obj.candidates.annotate(vote_count=Count("candidate_votes").order_by('-vote_count'))
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

