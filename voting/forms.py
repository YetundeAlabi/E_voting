from django import forms
from api.models import Candidate, Voter, Vote, Poll


class PollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = "__all__"