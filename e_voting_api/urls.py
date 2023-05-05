from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.UserSignUpView.as_view(), name='signup'),
    path('candidate/', views.CreateCandidateView.as_view(), name="candidate"),
    path('poll/', views.CreatePollView.as_view(), name="poll"),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path("login/", views.UserLoginAPIView.as_view(), name="login"),
    path("", views.TestView.as_view())


]
