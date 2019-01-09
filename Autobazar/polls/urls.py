from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('reg', views.reg, name='reg'),
    path('logout', views.logout, name='logout'),
    path('buy', views.buy, name='buy'),
    path('sell', views.sell, name='sell'),
    path('search', views.search, name='search'),
]