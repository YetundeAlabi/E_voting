import datetime

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.db.models.query import QuerySet
from django.urls import reverse
from accounts.models import User

now = datetime.datetime.now()


# Create your models here.
class Poll(models.Model):

    class PollObjects(models.Manager):
        def get_queryset(self) -> QuerySet:
            return super().get_queryset().filter(
                Q(start_time__lte=now) & Q(end_time__gte=now) & Q(is_deleted=False)
            )
        
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    start_time = models.TimeField(default=datetime.time(8, 0)) #poll starts at 8:00am
    end_time = models.TimeField(default=datetime.time(16, 0)) #poll ends at 4:00pm
    is_deleted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager() #default manager
    pollobjects = PollObjects() #custom manager
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        """ check if poll is active at current time """
        if self.start_time <= datetime.datetime.now().time() <= self.end_time:
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
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name ="candidate_votes")
    voted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("poll", "voted_by")


class Voter(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=False, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="voters")
    is_voted = models.BooleanField(default=False)

    def __str__(self):
        self.user.email

    def get_full_name(self):
        self.user.get_full_name()

    def cast_vote(self):
        if not self.is_voted:
            self.is_voted = True
            self.save()
            return True
        return False


