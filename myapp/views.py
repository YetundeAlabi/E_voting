from django.shortcuts import render
# Create your views here.


def dashboard(request):
    return render(request, 'myapp/index.html')

# def sigout(request):
#     return render(request, "frontend/register.html")

def create_voters(request):
    return render(request, "myapp/voters.html")

def login(request):
    return render(request, "myapp/pages-login.html")

def form(request):
    return render(request, "myapp/forms-elements.html")

def candidate(request):
    return render(request, "myapp/candidate.html")
