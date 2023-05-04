from django.urls import path
from e_voting_api import views

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
]
