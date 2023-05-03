from django.contrib import admin
from accounts.models import Voter
from e_voting.models import Poll, Candidate, Vote
# Register your models here.
admin.site.register(Poll)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Voter)
