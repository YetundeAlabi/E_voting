from django.db import models
from django.urls import reverse
from accounts.models import User
# from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Poll(models.Model):
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
    
    def get_absolute_url(self):
        return reverse("poll_detail", kwargs={"pk": self.pk})
    
    def get_total_vote(self):
        self.poll_votes.count()
    

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="e_voting/candidates", null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)

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




