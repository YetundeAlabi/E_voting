from django.urls import path
from accounts import views

urlpatterns = [
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path("auth/login/", views.UserLoginAPIView.as_view(), name="login"),
]