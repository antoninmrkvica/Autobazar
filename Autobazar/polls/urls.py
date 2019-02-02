from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('reg', views.reg, name='reg'),
    path('logout', views.logout, name='logout'),
    path('sell', views.sell, name='sell'),
    path('search', views.search, name='search'),
    path('viewmodels', views.viewmodels, name='viewmodels'),
    path('view', views.view, name='view'),
    path('edit_car', views.edit_car, name='edit_car'),
    path('remove_image', views.remove_image, name='remove_image'),
    path('delete_car', views.delete_car, name='delete_car'),
    path('send_password', views.send_password, name='send_password'),
    path('change_password', views.change_password, name='change_password'),
    path('acc', views.acc, name='acc'),
    path('buy_car', views.buy_car, name='buy_car'),
]