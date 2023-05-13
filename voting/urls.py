from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from voting import views
from django.urls import handler404
from .views import custom_404

handler404 = custom_404

app_name = "voting"
urlpatterns = [
    path("", views.index, name="index"),
    path("polls/create", views.PollCreateView.as_view(), name="create-poll"),
    path("candidates/create", views.CandidateCreateView.as_view(), name="create-candidate"),
    path("voters/create", views.VoterCreateView.as_view(), name="create-voter"),
    path("polls/<int:pk>/", views.PollDetailView.as_view(), name="poll-info"),
    path('polls/<int:poll_id>/vote/', views.record_vote_view, name='record-vote'),
]
#     path('polls/<int:pk>/delete/', views.PollDestroyView.as_view(), name='poll_delete'),
#     path('polls/<int:pk>/voters/', views.PollVoterListCreateView.as_view(), name='poll_voters'),
#     path('polls/<int:pk>/voters/<int:voter_pk>/', views.VoterPollView.as_view(), name='voter_poll'),
#     # path('polls/<int:pk>/voter/', views.AddVoterToPollView.as_view(), name='add_poll_voters'),
#     path('polls/<int:pk>/voters/<int:voter_pk>/delete/', views.VoterDestroyView.as_view(), name='remove_voter'),
    path('polls/<int:pk>/import/', views.VoterImportView.as_view(), name='import_voters'),
#     path('polls/<int:pk>/candidates/', views.CandidateListCreateView.as_view(), name='list_create_candidate'),
#     path('polls/<int:pk>/candidates/<int:candidate_pk>/vote/', views.CreateVoteView.as_view(), name='create_vote'),
#     path('polls/<int:pk>/result/', views.PollResultView.as_view(), name='poll_result'),
#     path('voters/', views.VoterListView.as_view(), name='voter_list'),
#     # path('voters/<int:pk>/', views.VoterPollListView.as_view(), name='voters_polls'),
#     # path('polls/<int:pk>/voters/<int:voter_pk>/', views.VoterDetailView.as_view(), name="voter_detail"),
#     path("send-email/", views.SendPollEmailView.as_view(), name="send-email")
# ]


