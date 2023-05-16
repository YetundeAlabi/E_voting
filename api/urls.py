from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api import views

schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="Voting App",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@e_voting.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
app_name= "api" 

urlpatterns = [
    path('polls/', views.PollListCreateView.as_view(), name='polls'),
    path('polls/<int:pk>/', views.PollDetailView.as_view(), name='poll_detail'),
    path('polls/<int:pk>/delete/', views.PollDestroyView.as_view(), name='poll_delete'),
    path('polls/<int:pk>/voters/', views.PollVoterView.as_view(), name='poll_voters'),
    path('polls/<int:pk>/voters/<int:voter_pk>/delete/', views.VoterDestroyView.as_view(), name='remove_voter'),
    path('polls/<int:pk>/import/', views.VoterImportView.as_view(), name='import_voters'),
    path('polls/<int:pk>/candidates/', views.CandidateListCreateView.as_view(), name='list_create_candidate'),
    path('polls/<int:pk>/candidates/<int:candidate_pk>/vote/', views.CreateVoteView.as_view(), name='create_vote'),
    path('polls/<int:pk>/result/', views.PollResultView.as_view(), name='poll_result'),
    path('voters/', views.VoterListView.as_view(), name='voter_list'),
    path('polls/<int:pk>/voters/<int:voter_pk>/', views.VoterDetailView.as_view(), name="voter_detail"),
    path("send-email/", views.SendPollEmailView.as_view(), name="send-email"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
