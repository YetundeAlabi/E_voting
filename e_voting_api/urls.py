from django.urls import path
from e_voting_api import views

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='create'),
    path('candidate/', views.CreateCandidateView.as_view(), name="candidate"),
    path('poll/', views.CreatePollView.as_view(), name="poll")

]
