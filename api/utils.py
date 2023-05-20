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
    def send_poll_email(voters, current_site):
        
        for voter in voters:
            poll_id = voter.poll.id
            voter_id = voter.uuid
            voter_email = voter.email
            
            voter_link = reverse('frontend:vote', args=[poll_id, voter_id])

            # Update the voter to mark that their poll email has been sent
            voter.email_sent = True
            voter.save()
            print(voter)
            # Send the poll email to the voter
            try:
                send_mail(
                    subject='Poll Notification',
                    message=f'Please participate in the poll. Click the link below:\n\n{current_site}{voter_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[voter_email],
                    fail_silently=True,
                )
            except smtplib.SMTPException as e:
                print(f"An error occured: {e}")
            
    

