import smtplib
import datetime

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.mail import send_mail
from api.models import Voter

# User = get_user_model()
# users = User.objects.filter(voters__isnull=False).distinct()


class Util:

    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(
                subject=data['email_subject'],
                body=data['email_body'],
                from_email=settings.EMAIL_HOST_USER,
                to=[data['to_email']]
            )
            email.send()
        except smtplib.SMTPException as e:
            print(f"An error occured: {e}")

    @staticmethod
    def send_poll_email():
        current_time = datetime.datetime.now()
        voters = Voter.objects.filter(polls__start_time__lte=current_time, email_sent=False)
        """ update voter email_sent field """

        for voter in voters:
            voter_email = voter.email
            poll_link = reverse('poll_detail', args=[voter.poll.id])  
            # Update the voter to mark that their poll email has been sent
            voter.email_sent = True
            voter.save()

            # Send the poll email to the voter
            send_mail(
                subject='Poll Notification',
                message=f'Please participate in the poll. Click the link below:\n\n{settings.BASE_URL}{poll_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[voter_email],
                fail_silently=True,
            )
       
        




