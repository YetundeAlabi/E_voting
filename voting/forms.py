from django import forms
from api.models import Candidate, Voter, Poll
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



now = timezone.now().time()

class PollUpdateForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = ["name", "description","start_time", "end_time"]
        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start time': forms.TimeInput(attrs={'placeholder': 'start time'}),
            'end time': forms.TimeInput(attrs={'placeholder': 'end time'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        

        if now > start_time:
            raise ValidationError("Poll has already started. Start time can not be updated") 



# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class VoterUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')
