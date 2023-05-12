from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "myapp"
urlpatterns = [
    path('forms/', views.form, name="form"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('candidates', views.candidate, name='candidate'),
    path('logout', views.signout, name='signout'),
    path("import-voters", views.import_voters, name='import-voters'),
    path('create-voters', views.create_voters, name='create-voters'), 
    path("", views.login, name="login")
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
