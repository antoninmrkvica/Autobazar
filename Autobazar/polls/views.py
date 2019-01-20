from django.shortcuts import render, redirect
from .models import User, Car
import datetime
from django.core.files.storage import FileSystemStorage

cars = Car.objects.all()
# list for sidenav
car_model_list = {}

for car in cars:
    car_model_list[car.mark.strip().upper()] = set()
for car in cars:
    car_model_list[car.mark.strip().upper()].add(car.model.strip().upper())

# sort at the end
sorted_dict = {}
for item in sorted(car_model_list):
    sorted_dict.update({item: car_model_list[item]})


# Create your views here.

def logged(req):
    if (req.session.get('user_id')):
        return True
    else:
        return False


def index(request):
    # print(Car.objects.all().values())

    return render(request, "./index.html",
                  {"logged": logged(request), "cars": Car.objects.all(), "car_list": sorted_dict})


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
    parameters = [["znacka", "Značka"], ["model", "Model"],
                  ["motorizace", "Motorizace"], ["vykon", "Výkon [kw]"], ["tachometr", "Tachometr"],
                  ["cena", "Cena"], ["datum_vyroby", "Datum výroby"], ["fuel_type", "Typ paliva"]]

    if request.method == "POST":
        spec_params = []
        for item in parameters:
            spec_param = request.POST.get(item[0])
            if not spec_param:
                spec_param = "null"
            spec_params.append(spec_param)
        perform = spec_params[3]
        if perform != "null":
            perform = str(float(perform) * 1.34102209)
        new_car = Car(mark=spec_params[0], model=spec_params[1], motorization=spec_params[2],
                      performance_kw=spec_params[3], performance_hp=perform,
                      killometres=spec_params[4], price=spec_params[5],
                      manufacture_date=spec_params[6],
                      owner=User.objects.filter(id=request.session.get('user_id'))[0],
                      add_date=datetime.datetime.now(), fuel_type=spec_params[7], description=request.POST.get('popis'),
                      repair=request.POST.get("opravy"), defects=request.POST.get("poskozeni"))
        new_car.save()
        imgs = request.FILES.getlist('files')
        for img in imgs:
            new_car.set_image("./media/" + str(new_car.id) + "/" + img.name)
            fs = FileSystemStorage(location="./polls/media/" + str(new_car.id))
            fs.save(img.name, img)
        new_car.save()
        return redirect("index")
    return render(request, "./sell.html",
                  {"logged": logged(request),
                   "car_param": parameters})


def search(request):
    return render(request, "./search.html", {"logged": logged(request)})


def viewmodels(request):
    mark = request.GET.get("mark")
    model = request.GET.get("model")

    cars_for_filter = Car.objects.all()
    filtered_cars = []
    for carf in cars_for_filter:
        if carf.mark.strip().upper() == mark and carf.model.strip().upper() == model:
            filtered_cars.append(carf)

    return render(request, "./index.html",
                  {"logged": logged(request), "cars": filtered_cars, "car_list": sorted_dict})


def view(request):
    car_id = request.GET.get('car_id')
    user = User.objects.filter(id=request.session.get('user_id'))
    return render(request, "./view.html",
                  {"logged": logged(request), "car_list": sorted_dict, "car": Car.objects.filter(id=car_id)[0],
                   "user": user[0]})
