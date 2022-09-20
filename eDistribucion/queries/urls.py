from django.urls import path

from . import views

urlpatterns = [
    path('', views.LoginApp.as_view(), name='index'),
    path('home', views.HomeApp.as_view(), name='home'),
    path('cycles/<item>', views.CyclesApp.as_view(), name='cycles'),
    path('interval/<item>', views.IntervalApp.as_view(), name='interval'),
    path('choose/<item>', views.ChooseApp.as_view(), name='choose'),
]