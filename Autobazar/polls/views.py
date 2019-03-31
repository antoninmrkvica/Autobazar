from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from .models import User, Car, Comment
import datetime
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import re

cars = Car.objects.all()


def sidenav_gener():
    # list for sidenav
    sorted_dict.clear()
    car_model_list = {}
    cars = Car.objects.all()
    if cars:
        for car in cars:
            car_model_list[car.mark.strip().upper()] = set()
        for car in cars:
            car_model_list[car.mark.strip().upper()].add(car.model.strip().upper())

        # sort at the end

        for item in sorted(car_model_list):
            sorted_dict.update({item: car_model_list[item]})


# generate sidenav_gener() after start and every time while new car is added to be sold or exists car is removed
sorted_dict = {}

# zakomentarovat pri vytvareni databaze
# sidenav_gener()
# nepotrebne - obejito pomoci prvniho prihlaseni na strance
first_start = True

parameters = [["znacka", "Značka"], ["model", "Model"],
              ["objem", "Objem motoru [L]"], ["turbo", "Turbo"], ["vykon", "Výkon [kW]"], ["tachometr", "Tachometr [km]"],
              ["cena", "Cena [Kč]"], ["datum_vyroby", "Rok výroby"], ["fuel_type", "Typ paliva"]]

marks = ['ALFA ROMEO', 'AUDI', 'BMW', 'CHEVROLET', 'CITROËN', 'DACIA', 'FIAT', 'FORD', 'HONDA', 'HYUNDAI', 'JEEP',
         'KIA',
         'LAND ROWER', 'MAZDA', 'MERCEDES-BENZ', 'MITSUBISHI', 'NISSAN', 'OPEL', 'PEUGEOT', 'RENAULT', 'SEAT', 'ŠKODA',
         'SUBARU', 'SUZUKI', 'TOYOTA', 'VOLVO', 'VOLKSWAGEN', 'JINÉ']
models = ['', '']


def current_user(user_id):
    return User.objects.filter(id=user_id).last()


# views ||

def index(request):
    # print(Car.objects.all().values())
    global first_start
    if first_start:
        sidenav_gener()
        first_start = False
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
            if len(list(User.objects.all())) == 0:
                new_user.is_admin = True
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
        perform = spec_params[4]
        if perform != "null":
            perform = str(round(float(perform) * 1.34102209))
        new_car = Car(mark=spec_params[0], model=spec_params[1], engine_capacity=spec_params[2], turbo=spec_params[3],
                      performance_kw=spec_params[4], performance_hp=perform,
                      killometres=spec_params[5], price=spec_params[6],
                      manufacture_date=spec_params[7],
                      owner=User.objects.filter(id=request.session.get('user_id'))[0],
                      add_date=datetime.datetime.now(), fuel_type=spec_params[8], description=request.POST.get('popis'),
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
                   "car_param": parameters, "marks": marks})


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
        perform = spec_params[4]
        if perform != "null":
            perform = str(round(float(perform) * 1.34102209))
        car.update(mark=spec_params[0], model=spec_params[1], engine_capacity=spec_params[2], turbo=spec_params[3],
                   performance_kw=spec_params[4], performance_hp=perform,
                   killometres=spec_params[5], price=spec_params[6],
                   manufacture_date=spec_params[7],
                   owner=User.objects.filter(id=request.session.get('user_id'))[0],
                   add_date=datetime.datetime.now(), fuel_type=spec_params[8], description=request.POST.get('popis'),
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
    print(car)
    current_user = User.objects.filter(id=request.session.get('user_id'))[0]
    if current_user == car.last().owner or current_user.is_admin:
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
            text = 'Uživatelské jméno: ' + user.last().username + '\n Heslo: ' + user.last().password
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


def buy_car(request):
    user = current_user(request.session.get('user_id'))
    car_id = request.GET.get('car_id')
    url = request.GET.get('url')
    car = Car.objects.filter(id=car_id)
    car.update(buyer=user)
    car.last().save()
    send_mail(
        'Autobazar - koupě automobilu',
        "Dobrý den,\nUživatel " + user.username + " (email: " + user.email + ", tel: " + user.phone + ") chce odkoupit Váš automobil: " + url + ".\nProsím Vás kontaktujte uživatele na email nebo telefon pro dokončení obchodu.\nPo uskutečnění obchodu potvrďte odkup automobilu na stránkách autobazaru pro odstranění inzerátu.\nDěkuji Vám za užívání mého webu,\nAutobazar Mrkvica",
        'autobazarmrkvica@gmail.com',
        [car.last().owner.email],
        fail_silently=False,
    )
    return HttpResponse(
        "Byl poslán email prodejci s vašimi kontaktními údaji(email, telefon). Vyčkejte až se vám majitel ozve.")


def profile(request):
    user_id = request.GET.get('user_id')
    user = current_user(user_id)
    comment_list = list(Comment.objects.filter(receiver=user))
    return render(request, "./profile.html",
                  {"user": current_user(request.session.get('user_id')), "profile": user, "car_list": sorted_dict,
                   "comment_list": comment_list})


def add_comment(request):
    comment = request.GET.get('comment')
    if comment:
        user_id = request.GET.get('user_id')
        comm = Comment(author=current_user(request.session.get('user_id')),
                       receiver=User.objects.filter(id=user_id).last(),
                       text=comment, date=datetime.datetime.now())
        comm.save()
        return HttpResponse("Byl přidán komentář.")
    return HttpResponse("Bohužel něco se nepovedlo.")


def remove_comment(request):
    comment_id = request.GET.get('comment_id')
    Comment.objects.filter(id=comment_id).delete()
    return HttpResponse("ok")


def search(request):
    allcars = list(Car.objects.all())
    price = 0
    killometres = 0
    mindate = 10000
    maxdate = 0
    for car in allcars:
        if price < int(car.price.replace(" ", "")):
            price = int(car.price.replace(" ", ""))
        if killometres < int(car.killometres.replace(" ", "")):
            killometres = int(car.killometres.replace(" ", ""))
        cardate = int(re.findall("[0-9]{4}", car.manufacture_date)[0])
        if cardate < mindate:
            mindate = cardate
        if cardate > maxdate:
            maxdate = cardate
    if request.method == "POST":
        pricemin = int(request.POST.get('pricemin'))
        pricemax = int(request.POST.get('pricemax'))
        datemin = int(request.POST.get('datemin'))
        datemax = int(request.POST.get('datemax'))
        kmmin = int(request.POST.get('kmmin'))
        kmmax = int(request.POST.get('kmmax'))
        for car in cars:
            date = int(re.findall("[0-9]{4}", car.manufacture_date)[0])
            if date < datemin or date > datemax or int(car.price.replace(" ", "")) < pricemin or int(car.price.replace(" ", "")) > pricemax or int(car.killometres.replace(" ", "")) < kmmin or int(car.killometres.replace(" ", "")) > kmmax:
                allcars.remove(car)
        return render(request, "./search.html",
                      {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict, "cars": allcars,
                       "maxprice": price, "maxkm": killometres, "mindate":mindate, "maxdate":maxdate
                       })
    return render(request, "./search.html",
                  {"user": current_user(request.session.get('user_id')), "car_list": sorted_dict, "cars": allcars,
                   "maxprice": price, "maxkm": killometres, "mindate":mindate, "maxdate":maxdate})

