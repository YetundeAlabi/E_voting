from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'frontend/index.html')

def signup(request):
    return render(request, "frontend/register.html")

def login(request):
    return render(request, "frontend/login.html")

def vote(request, poll_id, voter_id):
    context = {
        "poll_id": poll_id,
        "voter_id": voter_id
    }
    return render(request, "frontend/vote-page.html", context)


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES[""]