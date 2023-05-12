from django.urls import path
from frontend import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "frontend"
urlpatterns = [
    path('polls/', views.index, name="index"),
    path('', views.signup, name='signup'),
    path("login/", views.login, name="login")


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
