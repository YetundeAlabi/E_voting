from django.urls import path
from api import views

urlpatterns = [
    path('polls/', views.PollListCreateView.as_view(), name='polls'),
    path('polls/<int:pk>/', views.PollDetailView.as_view(), name='poll_detail'),
    path('polls/<int:pk>/delete/', views.PollDestroyView.as_view(), name='poll_delete'),
    path('polls/<int:pk>/voters/', views.PollVoterView.as_view(), name='poll_voters'),
    # path('polls/<int:pk>/voter/', views.AddVoterToPollView.as_view(), name='add_poll_voters'),
    path('polls/<int:pk>/voters/<int:voter_pk>/delete/', views.VoterDestroyView.as_view(), name='remove_voter'),
    path('polls/<int:pk>/import/', views.VoterImportView.as_view(), name='import_voters'),
    path('polls/<int:pk>/candidates/', views.CandidateListCreateView.as_view(), name='list_create_candidate'),
    path('polls/<int:pk>/candidates/<int:candidate_pk>/vote/', views.CreateVoteView.as_view(), name='create_vote'),
    path('polls/<int:pk>/result/', views.PollResultView.as_view(), name='poll_result'),
    path('voters/', views.VoterListView.as_view(), name='voter_list'),
    # path('voters/<int:pk>/', views.VoterPollListView.as_view(), name='voters_polls'),
]