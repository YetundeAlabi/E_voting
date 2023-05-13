import csv
import smtplib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView,UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View

from .forms import PollUpdateForm, VoterUploadForm
from api.models import Poll, Voter, Candidate, Vote
# Create your views here.

def index(request):
    return HttpResponse("Hello world")

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f"You are now logged in as {email}.")
            return redirect("main:homepage")
        else:
            messages.error(request,"Invalid username or password.")
            return render(request, 'login.html', {'error': 'Invalid credentials'})		
    return render(request=request, template_name="voting/login.html")


def logout_view(request):
    logout(request)
    # Redirect to a success page.


class SignupView(CreateView):
    template = 'signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')


class PollListView(ListView):
    model = Poll


class PollDetailView(DetailView):
    model = Poll


class PollCreateView(CreateView):
    model = Poll
    template_name = "voting/poll_form.html"
    fields = ["name", "description","start_time", "end_time"]



class PollUpdateView(UpdateView):
    model = Poll
    template_name = 'poll_update.html'
    fields = ['start_time', 'end_time']

    def get_object(self, queryset=None):
        obj = get_object_or_404(Poll, pk=self.kwargs['pk'])
        return obj

    def form_valid(self, form):
        poll = form.save(commit=False)

        # Check if the poll has started
        if poll.has_started():
            # If poll has started, return a response indicating it cannot be updated
            return redirect('voting:poll-detail', pk=poll.pk)

        # Check if the poll is active
        if poll.is_active:
            # If poll is active, update only the end time
            poll.end_time = form.cleaned_data['end_time']
        else:
            # If poll is not active, update both start time and end time
            poll.start_time = form.cleaned_data['start_time']
            poll.end_time = form.cleaned_data['end_time']

        poll.save()
        return redirect('voting:poll-detail', pk=poll.pk)


class PollDeleteView(UpdateView):
    model = Poll
    template_name = 'poll_delete.html'
    fields = []

    def get_object(self, queryset=None):
        obj = get_object_or_404(Poll, pk=self.kwargs['pk'])
        return obj

    def form_valid(self, form):
        poll = form.save(commit=False)
        poll.is_deleted = True
        poll.save()
        return redirect('voting:poll-list')


class CandidateCreateView(CreateView):
    model = Candidate
    fields = "__all__"


class CandidateListView(ListView):
    model = Candidate

    def get_queryset(self):
        return Candidate.objects.filter(poll_id=self.kwargs["pk"])


class VoterCreateView(CreateView):
    model = Voter
    fields = "__all__"


class VoterUploadView(View):
    def get(self, request, poll_id):
        form = VoterUploadForm()
        return render(request, 'upload_voters.html', {'form': form})

    def post(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise Http404("Poll does not exist")

        # Check if the poll is active
        if poll.is_active:
            error_message = "Cannot import voters when the poll is active."
            return render(request, 'import_voters.html', {'form': VoterUploadForm(), 'error': error_message})

        form = VoterUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(decoded_file.splitlines(), delimiter=',')
            expected_headers = ["first_name", "last_name", "email", "phone_number"]
            headers = csv_data.fieldnames  
            if headers != expected_headers:
                raise ValueError('Invalid CSV file. Headers do not match. Expected headers: {}'.format(', '.join(expected_headers)))
            for row in csv_data:
                
                Voter.objects.create(poll=poll, first_name=row["first_name"], last_name=row["last_name"],
                                      email=row['email'], phone_number=row['phone_number'])
            
                messages.success(request, "Import successful")
            return redirect('voting:poll-detail', poll_id=poll_id)  # Redirect to poll detail page after successful upload

        return render(request, 'import_voters.html', {'form': form})


class SendEmailView(View):

    def get(self, request):
        voters = Voter.objects.all()
        print(voters)
        current_site = get_current_site(request).domain
        
        for voter in voters:
            poll_id = voter.poll.id
            voter_id = voter.id
            voter_email = voter.email
            # poll_link = reverse('frontend:vote', kwargs={'pk': poll_id, 'voter_pk': voter_id})
            voter_link = reverse('frontend:vote', args=[poll_id, voter_id])
 
            # Send the poll email to the voter
            try:
                send_mail(
                    subject='Poll Notification',
                    message=f'Please participate in the poll. Click the link below:\n\n{current_site}{voter_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[voter_email],
                    fail_silently=True,
                )
            except smtplib.SMTPException as e:
                print(f"An error occured: {e}")

            finally:
                Voter.objects.values_list("email", flat=True).update(email_sent=True)
     

def voter_detail_view(request, pk, voter_pk):
    try:
        voter = Voter.objects.get(id=voter_pk)
        poll = voter.poll
        candidates = poll.candidates.all()
        context = {
            'poll': poll,
            'voter': voter,
            'candidates': candidates,
        }
        return render(request, 'poll_voter_detail.html', context)

    except Voter.DoesNotExist:
        raise Http404
        

def vote_view(request, poll_id, voter_id): 
    voter = get_object_or_404(Voter, id=voter_id)
    poll = voter.poll
    # candidates = Candidate.objects.filter(poll=poll)

    # if request.method == 'POST':
    #     candidate_id = request.POST.get('candidate')
    #     candidate = get_object_or_404(Candidate, pk=candidate_id)
    #     voter = get_object_or_404(Voter, uuid=voter.id)  

    try:
        selected_candidate = poll.candidates.get(pk=request.POST["candidate"])

    except (KeyError, Candidate.DoesNotExist):
    # Redisplay the question voting form.
        return render(
        request,
        "poll_voter_detail.html",
        {
        "poll": poll,
        "error_message": "You didn't select a candidate.",
        },
        )
    # Check if the voter has already voted for this poll
    if Vote.objects.filter(poll=poll, voted_by=voter).exists():

        return redirect('voting:already-voted')

    # Create a new vote
    vote = Vote(poll=poll, candidate=selected_candidate, voted_by=voter)
    vote.save()

    # Increment the vote count for the candidate
    selected_candidate.vote_count += 1
    selected_candidate.save()

    # Redirect to a success page or any other desired page
    # return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    return HttpResponseRedirect('voting:vote-success')

    return render(request, 'vote_form.html', {'poll': poll, 'candidates': candidates})
