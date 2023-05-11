from django.shortcuts import render
# Create your views here.


def dashboard(request):
    return render(request, 'myapp/index.html')

# def signup(request):
#     return render(request, "frontend/register.html")

def login(request):
    return render(request, "myapp/pages-login.html")

def form(request):
    return render(request, "myapp/forms-elements.html")
