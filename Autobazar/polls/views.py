from django.shortcuts import render, redirect
from .models import User, Car


# Create your views here.

def logged(req):
    if (req.session.get('user_id')):
        return True
    else:
        return False


def index(request):
    return render(request, "./index.html", {"logged": logged(request)})


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


def buy(request):
    return render(request, "./buy.html", {"logged": logged(request)})


def sell(request):
    if request.method == "POST":
        return redirect("index")
    return render(request, "./sell.html",
                  {"logged": logged(request),
                   "car_param": [["znacka", "Značka"], ["model", "Model"],
                                 ["motorizace", "Motorizace"], ["tachometr", "Tachometr"],
                                 ["cena", "Cena"], ["datum_vyroby", "Datum výroby"],
                                 ["vyhrivana_sedadla", "Vyhřívaná sedadla"],
                                 ["airbag", "Airbag"],
                                 ["mlhovky", "Mlhovky"],
                                 ["denni_sviceni", "Denní svícení"],
                                 ["rezervni_kolo", "Rezervní kolo"],
                                 ["vyhrivane_celni_sklo", "Vyhřívané čelní sklo"],
                                 ["vyhrivana_zrcatka", "Vyhřívaná zrcátka"],
                                 ["delena_zadni_sedadla", "Dělená zadní sedadla"],
                                 ["klimatizace", "Klimatizace"]]})

def search(request):
    return render(request, "./search.html", {"logged": logged(request)})