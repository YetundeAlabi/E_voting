from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path("auth/login/", views.UserLoginAPIView.as_view(), name="login"),
    path('polls/', views.PollListView.as_view(), name="poll"),
    path('polls/<int:pk>/candidate', views.CandidateListView.as_view(), name="candidate-list"),
    path('polls/<int:pk>/', views.PollDetailView.as_view(), name="poll_detail"),
    path('voters/', views.AddVoterToPollView.as_view(), name="poll_voters"),
    path('polls/<int:pk>/voter/', views.VoterRegistrationView.as_view(), name="register_voters")
   
    # path("", views.TestView.as_view())


]
