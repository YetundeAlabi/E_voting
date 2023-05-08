import csv
import logging
from logging import Logger, LoggerAdapter
from django.shortcuts import get_object_or_404
import jwt
from datetime import datetime

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from rest_framework import generics
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from . import serializers
from .serializers import (
    UserSerializer, 
    PollSerializer, 
    CandidateSerializer, 
    UserLoginSerializer, 
    EmailVerificationSerializer 
)
from accounts.models import User
from .utils import Util
from e_voting.models import Candidate, Poll, Vote, Voter
from e_voting_api.permissions import IsAdminOrReadOnly

logger = logging.getLogger(__name__)

class UserSignUpView(CreateAPIView):
    """Create a new user in the system"""
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            user_data = serializer.data

            token = RefreshToken.for_user(user)
            refresh = {
                'refresh': str(token),
                'access': str(token.access_token),
            }
            current_site = get_current_site(request).domain
            relative_link = reverse("email-verify")

            absurl = f'http://{current_site}{relative_link}?token={refresh["access"]}'
            email_body = f'Hi {user.first_name} Use the link below to verify your email \n{absurl}'
            data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify your email"}
            Util.send_email(data)
            
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmail(GenericAPIView):
    """ An endpoint to verify if user email is authentic before login"""
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id = payload['user_id'])  
            if not user.is_verified:  
                user.is_verified = True
                user.save()
            return Response({"email": 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSigntureError as identifier:
            return Response({"error": 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({"error": 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        
        return Response(data, status=status.HTTP_200_OK)


class PollListView(generics.ListCreateAPIView):
    serializer_class = serializers.PollSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return Poll.pollobjects.all() #only get active polls


class PollDetailView(generics.RetrieveUpdateAPIView):
    queryset = Poll.objects.all() #only get active polls
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
    queryset = Poll.objects.all()
    serializer_class = serializers.PollDetailSerializer
    permission_classes = [IsAdminUser]


    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message":"poll successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
  

class CandidateCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        poll = Poll.objects.get(id=self.kwargs["pk"])
        serializer.save(poll=poll)
        return super().perform_create(serializer)
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(response.data, status=201)

    

class VoterListView(generics.ListAPIView):
    serializer_class = serializers.VoterSerializer
    queryset = Voter.objects.all()
    # permission_classes = [I]


class VoterPollListView(generics.ListAPIView):
    serializer_class = serializers.VoterDetailSerializer
    queryset = Voter.objects.all()

    def get_queryset(self):
        return Voter.objects.filter(user=self.request.user).all()

    # def get_object(self):
    #     obj = self.polls.filter(user=)


class ListPollVoterView(generics.ListAPIView):
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Voter.objects.filter(poll_id = self.kwargs["pk"])


class AddVoterToPollView(generics.CreateAPIView):
    serializer_class = serializers.VoterEmailSerializer
    permission_classes = [IsAdminUser]
    # queryset = Voter.objects.all()

    
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
    queryset = Poll.objects.all()
    serializer_class = serializers.VoterSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return Poll.objects.filter(voters__id = self.kwargs["voter_pk"])
        

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_active:
            self.perform_destroy(instance)
            return Response({"message":"Voter successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message: Can't delete a voter on an active poll"})

# class VoterImportView(CreateAPIView):
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [IsAdminUser]
#     serializer_class = serializers.VoterEmailSerializer

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['poll_id'] = self.kwargs.get('pk')
#         print("got here")
#         print(context, "hello")
#         return context
    
#     def post(self, request, *args, **kwargs):
#         # csv_file = request.FILES.get('file')
#         serializer = serializers.FileImportSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         file = serializer.validated_data.get("file")
#         # file = serializer.save()
#         rows_with_errors = []
#         try:
#             decoded_file = file.read().decode('utf-8').splitlines()
#             reader = list(csv.DictReader(decoded_file))

#             with transaction.atomic():
#                 # for row in reader:
#                 for i, row in enumerate(reader, start=1):
#                     serializer = serializers.VoterEmailSerializer(data=reader, many=True, context=self.get_serializer_context())
#                     if serializer.is_valid():
#                         serializer.save()
#                         # voter_serializer = serializers.VoterSerializer(voter)
#                         # return Response(voter_serializer.data, status=status.HTTP_201_CREATED)
#                         # return Response({'status': 'success'})
#                     else:
#                         rows_with_errors.append(i)
#                         logger.error(f"Error importing row {i}: {serializer.errors}")
#                 if rows_with_errors:
#                     transaction.rollback()
#                     return Response({"error": f"Errors in rows {', '.join(map(str, rows_with_errors))}"}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response({'status': 'success'})
#         except Exception as e:
#             logger.error('An error occurred: %s', str(e))
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

        #                 Logger.error(f"Error importing row {row}: {serializer.errors}")
        #                 transaction.rollback()
        #                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VoterImportView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = serializers.FileImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")

        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            # Collect all the rows with errors instead of returning on the first error
            errors = []
            voters = []

            for row in reader:
                row_serializer = serializers.VoterEmailSerializer(data=row)

                if not row_serializer.is_valid():
                    errors.append({'row': row, 'errors': row_serializer.errors})
                    continue

                user = User.objects.filter(email=row['email']).first()

                if not user:
                    errors.append({'row': row, 'errors': {'email': ['User with this email does not exist']}})
                    continue

                poll_id = self.kwargs['pk']
                poll = Poll.objects.filter(id=poll_id).first()

                if not poll:
                    errors.append({'row': row, 'errors': {'poll_id': ['Poll with this ID does not exist']}})
                    continue

                # Check if voter already exists for this poll
                if Voter.objects.filter(user=user, poll=poll).exists():
                    errors.append({'row': row, 'errors': {'email': ['Voter with this user and poll ID already exists']}})
                    continue

                voter = Voter(user=user, poll=poll)
                voter.save()

            if errors:
                # If there are any errors, rollback the transaction and return a response with errors
                transaction.rollback()
                return Response({'status': 'failure', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            # If no errors, commit the transaction and return a success response
            transaction.commit()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class CandidateImportView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         file_obj = request.data['file']
#         if not file_obj.name.endswith('.csv'):
#             return Response({'error': 'File type not supported'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             decoded_file = file_obj.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
#             serializer = CandidateSerializer(data=reader, many=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class CreateStaffFromCSV(LoginRequiredMixin, PermissionRequiredMixin, View):
#     template_name = 'organization/staff_create_from_csv.html'
    
#     def get(self, request, *args, **kwargs):
#         form = CsvFileForm
#         context = {'form': form }
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         csv_file = request.FILES.get('file')
#         current_org = request.user.organization
#         slug = current_org.slug

#         if not csv_file:
#             messages.error(request, 'Please select a CSV file.')
#             return HttpResponseRedirect(reverse("organization:staff_create_csv", kwargs={'org_slug': slug }))

#         try:
#             decoded_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
#             with transaction.atomic():
#                 for row in reader:
#                     staff = Staff(
#                         first_name=row['first_name'],
#                         last_name=row['last_name'],
#                         personal_email=row['personal_email'],
#                         gender=row['gender'],
#                         username=row['username'],
#                         phone_number=row['phone_number'],
#                         date_of_birth=row['date_of_birth'],
#                         state_of_origin=row['state_of_origin'],
#                         staff_status=row['staff_status'],
#                         next_of_kin_name=row['next_of_kin_name'],
#                         next_of_kin_email=row['next_of_kin_email'],
#                         next_of_kin_phone_number=row['next_of_kin_phone_number'],
#                         dept_id=row['dept_id'],
#                         job_title_id=row['job_title_id'],   
#                     )
#                     try:
#                         staff.full_clean()
#                     except ValidationError as e:
#                         messages.error(request, f"Error on row {reader.line_num}: {e}")
#                         return HttpResponseRedirect(reverse("organization:staff_create_csv", kwargs={'org_slug': slug }))
#                     try:
#                         staff.work_email = f"{staff.first_name[0].lower()}{staff.last_name.lower()}@{current_org.company_email_domain}"
#                         staff.organization = current_org
#                         password = generate_password()
#                         user = User.objects.create_user(username=staff.username,
#                                     email=staff.work_email,
#                                     password=password,
#                                     )
#                         staff.user = user
#                         staff.save()
#                     except IntegrityError:
#                         transaction.rollback()
#                         messages.error(request, f"Error on row {reader.line_num}: Staff with username '{row['username']}' already exists.")
#                         return HttpResponseRedirect(reverse("organization:staff_create_csv", kwargs={'org_slug': slug }))
#         except csv.Error as e:
#             messages.error(request, f'Error processing CSV file: {e}')
#             return HttpResponseRedirect(reverse("organization:staff_create_csv", kwargs={'org_slug': slug }))
            

#         messages.success(request, 'Staff successfully created.')
#         subject = f"{current_org.name}: LOGIN CREDENTIALS"
#         message = f"Dear {staff.fullname()},\n\nWelcome to {current_org.name}.\n\nLogin to your dashboard using these credentials.\n\nUsername: {staff.username}\nPassword: {password}"
#         recipient_list = [staff.personal_email,]
#         # send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
#         return HttpResponseRedirect(reverse("organization:admin_dashboard",  kwargs={'org_slug': slug }))

#     def has_permission(self):
#         org_slug = self.kwargs['org_slug']
#         return self.request.user.organization.slug == org_slug



    

#     # def perform_create(self, serializer):
#     #     poll_id = self.kwargs.get('poll_id')
#     #     poll = Poll.objects.get(id=poll_id)
#     #     serializer.save(poll=poll)
    

class TestView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []

# class AddVoterToPollView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Voter.objects.all()
#     serializer_class = serializers.VoterSerializer

#     def post(self, request):
#         serializer = serializers.AddVoterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         voter = serializer.save()
#         voter_serializer = serializers.VoterSerializer(voter)
#         return Response(voter_serializer.data)


# class VoterRegistrationView(generics.ListCreateAPIView):
#     serializer_class = serializers.VoterSerializer
#     permission_classes = [IsAdminUser]
#     queryset = Voter.objects.all()

#     # def get_queryset(self):
#     #     return Voter.objects.filter(poll_id = self.kwargs["pk"])
    
#     # def post(self, request, *args, **kwargs):
#     #     serializer = serializers.VoterEmailSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     voter = serializer.save()
#     #     user = User.objects.get(email=voter)
#     #     # get the poll by id
#     #     poll_id = self.kwargs["pk"]
#     #     poll = Poll.objects.get(poll_id)
        
#     #     # check if voter already exists for this poll
#     #     if Voter.objects.filter(user=user, poll=poll).exists():
#     #         return Response({'error': 'Voter with the same user and poll id already exists.'}, 
#     #                         status=status.HTTP_400_BAD_REQUEST)
        
#     #     voter = Voter(user=user, poll=poll)
#     #     voter.save()
#     #     voter_serializer = serializers.VoterSerializer(voter)
#     #     return Response(voter_serializer.data)

# class AddVoterView(generics.)

# class VoterListCreateView(generics.ListCreateAPIView):
#     queryset = Voter.objects.all()
#     serializer_class = serializers.VoterSerializer
#     permission_classes = [IsAuthenticated]


# class VoterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Voter.objects.all()
#     serializer_class = serializers.VoterSerializer
#     permission_classes = [IsAuthenticated]


# class CandidateListView(generics.ListCreateAPIView):
#     serializer_class =  CandidateSerializer
#     permission_classes = [IsAdminUser, IsAuthenticated]
    

#     def get_queryset(self):
#         """filter candidates using poll id"""
#         queryset = Candidate.objects.filter(poll_id = self.kwargs.get("pk"))
#         return queryset
    
#     def get_serializer_context(self):
#         poll_id = self.kwargs.get('poll_id')
#         return {'poll_id': poll_id}
    


# 