from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from voting import views
# from django.urls import handler404
from .views import custom_404

app_name = "voting"
urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('polls/', views.PollListView.as_view(), name="poll-list"),
    path("polls/create", views.PollCreateView.as_view(), name="create-poll"),
    path("candidates/create", views.CandidateCreateView.as_view(), name="create-candidate"),
    path("voters/create", views.VoterCreateView.as_view(), name="create-voter"),
    path("polls/<int:poll_id>/", views.PollDetailView.as_view(), name="poll-detail"),
    path('polls/<int:pk>/update/', views.PollUpdateView.as_view(), name='poll-update'),
    path('polls/<int:pk>/delete', views.PollDeleteView.as_view(), name='poll-delete'),
    path('polls/<int:pk>/candidates/', views.CandidateListView.as_view(), name='list_create_candidate'),
    path('polls/<int:pk>/voters/<int:voter_pk>/delete/', views.VoterDeleteView.as_view(), name='remove_voter'),
    path('polls/<int:pk>/import/', views.VoterImportView.as_view(), name='import-voters'),
    path('polls/<int:pk>/voters', views.voter_detail_view, name="voter-detail"),
#  path('polls/<int:pk>/result/', views.PollResultView.as_view(), name='poll_result'),
    path('polls/<int:pk>/voters/<int:voter_pk>/vote', views.VoteView.as_view(), name="vote"),
    path("send-email/", views.SendEmailView.as_view(), name="send-email")
]
# handler404 = "views.custom_404"

