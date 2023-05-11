from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "myapp"
urlpatterns = [
    # path('signup/', views.UserSignUpView.as_view(), name='signup'),
    # path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    # path("auth/login/", views.UserLoginAPIView.as_view(), name="login"),
    # path('polls/', views.PollListView.as_view(), name="poll"),
    # path('polls/<int:pk>/candidate', views.CandidateCreateView.as_view(), name="create_candidate"),
    # path('polls/<int:pk>/', views.PollDetailView.as_view(), name="poll_detail"),
    # path('polls/<int:pk>/delete', views.PollDestroyView.as_view(), name="poll_detail"),
    # path('polls/<int:pk>/voters/', views.ListPollVoterView.as_view(), name="poll_voters"),
    # path('polls/<int:pk>/voter/', views.AddVoterToPollView.as_view(), name="add_poll_voters"),
    # path('polls/<int:pk>/voters/<int:voter_pk>/', views.VoterDestroyView.as_view(), name="remove_voter"),
    # path("voters/", views.VoterListView.as_view(), name="voterlist"),
    # path("voters/<int:pk>/", views.VoterPollListView.as_view(), name="voters_polls"),
    # path("polls/<int:pk>/import/", views.VoterImportView.as_view(), name="import_voters"),
    # path('polls/<int:pk>/candidate/<int:candidate_pk>/vote', views.CreateVoteView, name="crreate_vote")
    path('dashboard/forms/', views.form, name="form"),
    path('dashboard', views.dashboard, name='dashboard'),

    path("", views.login, name="login")

    # path("", views.TestView.as_view())


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)