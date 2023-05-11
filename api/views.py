import csv

from django.db import transaction

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model


from api import serializers
from accounts.models import User
from .utils import Util
from api.models import Candidate, Poll, Vote, Voter
from api.permissions import IsAdminOrReadOnly

# User = get_user_model()

class PollListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.PollSerializer
    permission_classes = [IsAdminOrReadOnly]
    # permission_classes = []

    def get_queryset(self):
        return Poll.pollobjects.all()  # only get active polls


# class PollListView(generics.ListAPIView):
#     serializer_class = serializers.PollSerializer
#     permission_classes = []

#     def get_queryset(self):
#         return Poll.objects.all()


class PollDetailView(generics.RetrieveUpdateAPIView):
    """ Endpoint that show details about active poll with user detail"""
    queryset = Poll.objects.all()  # only get active polls
    serializer_class = serializers.PollDetailSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

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
    """endpoint to get and create candidate for a poll"""

    queryset = Candidate.objects.all()
    serializer_class = serializers.CandidateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        poll = Poll.objects.get(id=self.kwargs["pk"])
        serializer.save(poll=poll)
        return super().perform_create(serializer)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(response.data, status=201)


class VoterListView(generics.ListAPIView):
    """ list of all voters """
    serializer_class = serializers.VoterSerializer
    queryset = Voter.objects.all()
    # permission_classes = [I]


class VoterPollListView(generics.ListAPIView):
    """ list all poll registered for by a voter """
    serializer_class = serializers.VoterDetailSerializer
    queryset = Poll.objects.all()

    def get_queryset(self):
        """ as voter can be vote on different polls, get all polls linked to one voter """
        return Voter.objects.filter(id=self.request.user.id).all()
    

# class VoterPollEmailView(generics.ListAPIView):
#     serializer_class = serializers.VoterDetailSerializer
#     queryset = User.objects.all()

#     def get_queryset(self):
#         query_set = super().get_queryset()
#         return query_set.filter(voters__isnull=False).distinct()



class ListPollVoterView(generics.ListAPIView):
    """ list all voters in a poll """
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Voter.objects.filter(poll_id=self.kwargs["pk"])


class AddVoterToPollView(generics.CreateAPIView):
    """add voters to poll through an admin"""
    serializer_class = serializers.VoterEmailSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['poll_id'] = self.kwargs.get('pk')
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        voter = serializer.save()
        voter_serializer = serializers.VoterSerializer(voter)
        return Response(voter_serializer.data, status=status.HTTP_201_CREATED)


class VoterDestroyView(generics.DestroyAPIView):
    """ delete voter """
    queryset = Poll.objects.all()
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Poll.objects.filter(voters__id=self.kwargs["voter_pk"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_active:
            self.perform_destroy(instance)
            return Response({"message": "Voter successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message: Can't delete a voter on an active poll"})


class VoterImportView(APIView):
    """ import voters using a csv"""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = serializers.FileImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")

        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            """Collect all the rows with errors instead of returning on the first error"""
            errors = []

            with transaction.atomic():
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
                    # If there are any errors, return a response with errors
                    return Response({'status': 'failure', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

                # If no errors, return a success response
                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        #     if errors:
        #         # If there are any errors, rollback the transaction and return a response with errors
        #         transaction.rollback()
        #         return Response({'status': 'failure', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        #     # If no errors, commit the transaction and return a success response
        #     transaction.commit()
        #     return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateVoteView(generics.CreateAPIView):
    serializer_class = serializers.VoteSerializer

    def post(self, request, *args, **kwargs):
        poll_id = self.kwargs["pk"]
        candidate_id = self.kwargs["candidate_pk"]

        try:
            """ get only active polls. Can't vote before start time"""
            poll = Poll.objects.get(id=poll_id)
            candidate = Candidate.objects.get(id=candidate_id)
            user = request.user
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


class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = Voter.objects.all()
    permission_classes = []
