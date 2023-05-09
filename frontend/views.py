from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'frontend/index.html')

def signup(request):
    return render(request, "frontend/register.html")