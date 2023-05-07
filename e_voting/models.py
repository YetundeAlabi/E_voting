import datetime

from django.db import models
from django.conf import settings
from django.urls import reverse
from accounts.models import User
# from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Poll(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    start_time = models.TimeField(default=datetime.time(8, 0)) #poll starts at 8:00am
    end_time = models.TimeField(default=datetime.time(16, 0)) #poll ends at 4:00pm
    is_deleted = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        """ check if poll is active at current time """
        if self.start_time >= datetime.now().time() <= self.end_time:
            return True  
        return False

    
    def get_absolute_url(self):
        return reverse("poll_detail", kwargs={"pk": self.pk})
    
    def get_total_vote(self):
        self.poll_votes.count()
    

class Candidate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="e_voting/candidates", null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, related_name="candidates")

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("candidate_detail", kwargs={"pk": self.pk})
    
    def get_vote_count(self):
        self.candidate_votes.count()
    

class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="poll_votes")
    choice = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name ="candidate_votes")
    voted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("poll", "voted_by")


class Voter(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=False, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="voters")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['poll'], name='unique_voter_poll')
        ]
    def __str__(self):
        self.user.email

    def get_full_name(self):
        self.user.get_full_name()



