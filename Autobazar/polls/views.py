from django.shortcuts import render, redirect
from .models import User

# Create your views here.

def index(request):
    if (request.session.get('user_id')):
        logged = True
    else:
        logged = False
    return render(request, "./index.html", {"logged": logged})


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        if username == "" or passwd == "":
            return render(request, "./login.html", {"msg": "Something is missing."})
        searched_user = User.objects.filter(username=username, password=passwd)
        if searched_user:
            request.session['user_id'] = searched_user[0].id
        else:
            return render(request, "./login.html", {"msg": "User isn't registered or wrong password."})
        return redirect("index")
    else:
        return render(request, "./login.html")


def reg(request):
    if request.method == "POST":
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        passwdconfirm = request.POST.get('passwdconfirm')
        if username == "" or passwd == "" or passwdconfirm == "":
            return render(request, "./reg.html", {"msg": "Something is missing."})
        elif passwd != passwdconfirm:
            return render(request, "./reg.html", {"msg": "Passwords don't match."})
        else:
            new_user = User(username=username, password=passwd)
            new_user.save()
            request.session['user_id'] = new_user.id
            return redirect("index")
    else:
        return render(request, "./reg.html", {"msg": ""})


def logout(request):
    del request.session['user_id']
    return redirect("index")