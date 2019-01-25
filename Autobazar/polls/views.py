from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from .models import User, Car
import datetime
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail

cars = Car.objects.all()


def sidenav_gener():
    # list for sidenav
    sorted_dict.clear()
    car_model_list = {}
    cars = Car.objects.all()
    for car in cars:
        car_model_list[car.mark.strip().upper()] = set()
    for car in cars:
        car_model_list[car.mark.strip().upper()].add(car.model.strip().upper())

    # sort at the end

    for item in sorted(car_model_list):
        sorted_dict.update({item: car_model_list[item]})


# generate sidenav_gener() after start and every time while new car is added to be sold or exists car is removed
sorted_dict = {}
sidenav_gener()

parameters = [["znacka", "Značka"], ["model", "Model"],
              ["motorizace", "Motorizace"], ["vykon", "Výkon [kw]"], ["tachometr", "Tachometr"],
              ["cena", "Cena"], ["datum_vyroby", "Datum výroby"], ["fuel_type", "Typ paliva"]]


# Create your views here.


def current_user(user_id):
    return User.objects.filter(id=user_id).last()


def index(request):
    # print(Car.objects.all().values())

    return render(request, "./index.html",
                  {"cars": Car.objects.all(), "car_list": sorted_dict,
                   "user": current_user(request.session.get('user_id'))})


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
            return render(request, "./login.html",
                          {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                           "msg": "Uživatelské jméno neexistuje nebo bylo zadáno špatné heslo."})
        return redirect("index")
    else:
        return render(request, "./login.html",
                      {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict})


def reg(request):
    if request.method == "POST":
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        passwdconfirm = request.POST.get('passwdconfirm')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        if username == "" or passwd == "" or passwdconfirm == "" or phone == "" or email == "":
            return render(request, "./reg.html", {"msg": "Musíte vyplnit všechna pole."})
        elif passwd != passwdconfirm:
            return render(request, "./reg.html", {"msg": "Hesla se musí shodovat."})
        elif User.objects.filter(username=username):
            return render(request, "./reg.html", {"msg": "Uživatelské jméno již existuje!!"})
        else:
            new_user = User(username=username, password=passwd, phone=phone, email=email)
            new_user.save()
            request.session['user_id'] = new_user.id
            return redirect("index")
    else:
        return render(request, "./reg.html",
                      {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict, "msg": ""})


def logout(request):
    del request.session['user_id']
    return redirect("index")


def sell(request):
    if request.method == "POST":
        spec_params = []
        for item in parameters:
            spec_param = request.POST.get(item[0])
            if not spec_param:
                spec_param = "null"
            spec_params.append(spec_param)
        perform = spec_params[3]
        if perform != "null":
            perform = str(round(float(perform) * 1.34102209))
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
        sidenav_gener()
        return redirect("index")
    return render(request, "./sell.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                   "car_param": parameters})


def search(request):
    return render(request, "./search.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict})


def viewmodels(request):
    mark = request.GET.get("mark")
    model = request.GET.get("model")

    cars_for_filter = Car.objects.all()
    filtered_cars = []
    for carf in cars_for_filter:
        if carf.mark.strip().upper() == mark and carf.model.strip().upper() == model:
            filtered_cars.append(carf)

    return render(request, "./index.html",
                  {"user": current_user(request.session.get('user_id')), "cars": filtered_cars,
                   "car_list": sorted_dict})


def view(request):
    car_id = request.GET.get('car_id')
    return render(request, "./view.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                   "car": Car.objects.filter(id=car_id)[0]})


def edit_car(request):
    if request.method == "POST":
        car_id = request.POST.get('car_id')
        car = Car.objects.filter(id=car_id)
        spec_params = []
        for item in parameters:
            spec_param = request.POST.get(item[0])
            if not spec_param:
                spec_param = "null"
            spec_params.append(spec_param)
        perform = spec_params[3]
        if perform != "null":
            perform = str(round(float(perform) * 1.34102209))
        car.update(mark=spec_params[0], model=spec_params[1], motorization=spec_params[2],
                   performance_kw=spec_params[3], performance_hp=perform,
                   killometres=spec_params[4], price=spec_params[5],
                   manufacture_date=spec_params[6],
                   owner=User.objects.filter(id=request.session.get('user_id'))[0],
                   add_date=datetime.datetime.now(), fuel_type=spec_params[7], description=request.POST.get('popis'),
                   repair=request.POST.get("opravy"), defects=request.POST.get("poskozeni"))
        imgs = request.FILES.getlist('files')
        car = car[0]
        for img in imgs:
            car.set_image("./media/" + str(car.id) + "/" + img.name)
            fs = FileSystemStorage(location="./polls/media/" + str(car.id))
            fs.save(img.name, img)
        car.save()
        sidenav_gener()
        return HttpResponseRedirect("view?car_id=" + car_id)
    car_id = request.GET.get('car_id')
    return render(request, "./edit_car.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                   "car": Car.objects.filter(id=car_id)[0],
                   "car_param": parameters})


def remove_image(request):
    car_id = request.GET.get('car_id')
    image_path = request.GET.get('image_path')
    car = Car.objects.filter(id=car_id)[0]
    car.remove_image(image_path)
    car.save()
    return HttpResponse('remove done!!')


def delete_car(request):
    id = request.GET.get('car_id')
    car = Car.objects.filter(id=id)
    current_user = User.objects.filter(id=request.session.get('user_id'))[0]
    if current_user == Car.owner or current_user.is_admin:
        car.delete()
    sidenav_gener()
    return redirect("index")


def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('oldpasswd')
        new_pass = request.POST.get('passwd')
        new_pass_conf = request.POST.get('passwdconfirm')
        user_id = request.session.get('user_id')
        user = User.objects.filter(id=user_id)
        if user.last().password == old_password and new_pass == new_pass_conf:
            user.update(password=new_pass)
            user.last().save()
            return redirect('acc')
        else:
            return render(request, "./change_password.html",
                          {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                           "msg": "Špatné staré heslo nebo se nová hesla neshodují"})

    return render(request, "./change_password.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict})


def acc(request):
    return render(request, "./acc.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict})


def send_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email)
        if email and user:
            text = 'Uživatelské jméno: '+user.last().username+'\n Heslo: ' + user.last().password
            send_mail(
                'Autobazar password',
                text,
                'autobazarmrkvica@gmail.com',
                [email],
                fail_silently=False,
            )
            return render(request, "./send_password.html",
                          {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                           "msg": "successful"})
        return render(request, "./send_password.html",
                      {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict,
                       "msg": "Failed"})

    return render(request, "./send_password.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict})
