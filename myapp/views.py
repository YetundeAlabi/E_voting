from django.shortcuts import render
# Create your views here.
from django.contrib.auth import logout


def signout(request):
    logout(request)
    # Redirect to a success page.

def dashboard(request):
    return render(request, 'myapp/index.html')

def create_voters(request):
    return render(request, "myapp/voters.html")

def login(request):
    return render(request, "myapp/pages-login.html")

def form(request):
    return render(request, "myapp/forms-elements.html")

def candidate(request):
    return render(request, "myapp/candidate.html")

def import_voters(request):
    return render(request, "myapp/voter-import.html")

