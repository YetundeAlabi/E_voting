import csv
from datetime import datetime

from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser



from api import serializers
from accounts.models import User
from api.models import Candidate, Poll, Vote, Voter
from api.permissions import IsAdminOrReadOnly
from api.utils import Util
# User = get_user_model()

class PollListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.PollListSerializer
    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = []

    def get_queryset(self):
        return Poll.objects.all()  # only get active polls


class PollDetailView(generics.RetrieveUpdateAPIView):
    """ Endpoint that show details about active poll with user detail"""
    queryset = Poll.objects.all()  # only get active polls
    serializer_class = serializers.PollDetailSerializer
    permission_classes = [IsAdminOrReadOnly]

    def put(self, request, *args, **kwargs):
        poll = self.get_object()
        serializer = self.get_serializer(poll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollDestroyView(generics.DestroyAPIView):
    """ Delete poll endpoint """
    queryset = Poll.objects.all()
    serializer_class = serializers.PollDetailSerializer
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "poll successfully deleted"}, status=status.HTTP_204_NO_CONTENT)


class CandidateListCreateView(generics.ListCreateAPIView):
    """List and create candidates registered on a poll"""
    serializer_class = serializers.CandidateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        poll_id = self.kwargs["pk"]
        return Candidate.objects.filter(poll_id=poll_id)

    def perform_create(self, serializer):
        poll_id = self.kwargs["pk"]
        poll = Poll.objects.filter(id=poll_id).first()

        if not poll:
            return Response({'error': 'Poll with this ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer.save(poll=poll)


class CandidateUpdateView(generics.UpdateAPIView):
    """Update a candidate on a poll"""
    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer
    permission_classes = [IsAdminUser]


    def get_object(self):
        candidate_id = self.kwargs['candidate_pk']
        return self.queryset.get(id=candidate_id)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Access the validated poll object from the serializer
        poll = serializer.validated_data.get('poll')

        # Check if the poll exists
        if not Poll.objects.filter(id=poll.id).exists():
            return Response({'error': 'Poll with this ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        self.perform_update(serializer)
        return Response(serializer.data)


class VoterListView(generics.ListAPIView):
    """ list of all voters """
    serializer_class = serializers.VoterSerializer
    queryset = Voter.objects.all()
   

class VoterPollView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = serializers.PollSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['voter_id'] = self.kwargs["voter_pk"]
        return context
       

class PollVoterListCreateView(generics.ListCreateAPIView):
    """List all voters in a poll and add voters to the poll through an admin"""
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Voter.objects.filter(poll_id=self.kwargs["pk"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['poll_id'] = self.kwargs.get('pk')
        return context

    def perform_create(self, serializer):
        poll_id = self.kwargs.get('pk')
        poll = Poll.objects.filter(id=poll_id).first()

        if not poll:
            return Response({'error': 'Poll with this ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if poll.is_active:
            return Response({'poll_id': ['Poll is still active']}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(poll=poll)


class VoterDestroyView(generics.DestroyAPIView):
    """ delete voter """
    queryset = Poll.objects.all()
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Poll.objects.filter(voters__id=self.kwargs["voter_pk"])

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_active:
            self.perform_destroy(instance)
            return Response({"message": "Voter successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message: Can't delete a voter on an active poll"})


class VoterImportView(APIView):
    """ import voters using a csv"""
    #parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = serializers.FileImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")

    
        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            """Collect all the rows with errors instead of returning on the first error"""
            errors = []

        
            for row in reader:
                row_serializer = serializers.VoterImportSerializer(data=row)

                if not row_serializer.is_valid():
                    errors.append(
                        {'row': row, 'errors': row_serializer.errors})
                    continue

                poll_id = self.kwargs['pk']
                poll = Poll.objects.filter(id=poll_id).first()

                if not poll:
                    errors.append({'row': row, 'errors': {'poll_id': [
                                    'Poll with this ID does not exist']}})
                    continue

                if poll.is_active:  # only add a poll before polls begin
                    return Response({'status': "Poll is still active"})

                email = row_serializer.validated_data['email']

                # Check if voter already exists for this poll
                if Voter.objects.filter(email=email, poll=poll).exists():
                    errors.append({'row': row, 'errors': {
                                    'email': ['Voter with this user and poll ID already exists']}})
                    continue
                
                    # Create the voter instance
                # voter = row_serializer.save(poll=poll)

                # Instantiate the voter object
                voter = Voter(**row_serializer.validated_data, poll=poll)
                voter.save()
                    
            if errors:
                transaction.rollback()
                # If there are any errors, return a response with errors
                return Response({'status': 'failure', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            # If no errors, return a success response
            transaction.commit()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        

class CreateVoteView(generics.CreateAPIView):
    serializer_class = serializers.VoteSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        poll_id = self.kwargs["pk"]
        candidate_id = self.kwargs["candidate_pk"]
        user = request.user

        try:
            """ get only active polls. Can't vote before start time"""
            poll = Poll.objects.get(id=poll_id)

            if not poll.is_active:
                return Response({"status": f"Poll has not yet started. Check back in {poll.start_time}"}, status=status.HTTP_425_TOO_EARLY)

            candidate = Candidate.objects.get(id=candidate_id)
            
            voter = Voter.objects.get(poll=poll, id=user.id)

            """ check if voter has voted """
            if voter.cast_vote():
                vote = Vote.objects.create(
                    poll=poll, candidate=candidate, voted_by=voter)
                serializer = serializers.VoteSerializer(vote)
                return Response({"success": "Thank you for voting"}, serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'This voter has already cast a vote for this poll.'}, status=status.HTTP_400_BAD_REQUEST)
        except Poll.DoesNotExist:
            return Response({'error': 'Poll does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Voter.DoesNotExist:
            return Response({'error': 'This user is not registered to vote in this poll.'}, status=status.HTTP_400_BAD_REQUEST)


class PollResultView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = serializers.PollResultSerializer


class PollWinnersView(generics.ListAPIView):
    """ get a list of polls that have been voted on """
    queryset = Poll.objects.filter(poll_votes__isnull=False).distinct()
    serializer_class = serializers.PollWinnerSerializer

    def get(self, request, *args, **kwargs):
        winners = []
        for poll in self.get_queryset():
            votes = Vote.objects.filter(poll=poll)
            winner = max(votes, key=lambda vote: vote.candidate_votes.count())
            winners.append(winner.candidate)
        serializer = self.get_serializer(winners, many=True)
        return Response(serializer.data)


class SendPollEmailView(APIView):
    authentication_classes = []
    permission_classes = [IsAdminUser]
    def get(self, request):
        voters = Voter.objects.all()
        print(voters)
        current_site = get_current_site(request).domain
        Util.send_poll_email(voters, current_site)

        return Response({'message': 'Poll emails sent successfully'})
    

# class TestView(generics.ListAPIView):
#     serializer_class = serializers.VoterSerializer
#     queryset = Voter.objects.all()
#     permission_classes = []
