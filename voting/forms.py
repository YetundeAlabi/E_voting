from django import forms
from api.models import Candidate, Voter, Poll

class PollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = "__all__"

class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = "__all__"

class VoterForm(forms.ModelForm):

    class Meta:
        model = Voter
        fields = "__all__"