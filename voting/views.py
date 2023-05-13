from typing import Any, Dict
from django.db import models
from django.shortcuts import render
from forms import PollForm, VoterForm, CandidateForm
from api.models import Poll, Voter, Candidate, Vote
from django.views.generic import ListView, DetailView
# Create your views here.

class PollListView(ListView):
    model = Poll


class PollDetailView(DetailView):
    model = Poll

    # def get_object(self):
    #     obj = self.get_object()
    #     return obj.candidate.all()
    
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        poll_candidates = Candidate.objects.filter(poll_id = self.id).all()
        context["candidates"] = poll_candidates