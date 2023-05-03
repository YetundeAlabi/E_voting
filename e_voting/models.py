from django.db import models
from accounts.models import User, Voter

# Create your models here.
class VotingPoll(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)
    updated_start_time = models.DateTimeField(auto_now=True)
    updated_end_time = models.DateTimeField(auto_now = True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="/images", null=True)

    def __str__(self):
        return self.name
    

class Vote(models.Model):
    poll = models.ForeignKey(VotingPoll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voted_by = models.ForeignKey(Voter, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("poll", "voted_by")


# class Voters(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=255)