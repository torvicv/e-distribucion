from django.urls import path

from . import views

urlpatterns = [
    path('', views.LoginApp.as_view(), name='index'),
    path('home', views.HomeApp.as_view(), name='home'),
    path('cycles/<item>', views.CyclesApp.as_view(), name='cycles'),
    path('interval/<item>', views.IntervalApp.as_view(), name='interval'),
    path('choose/<item>', views.ChooseApp.as_view(), name='choose'),
    path('chart', views.TemplateView.as_view(template_name='line_chart.html'), name='line_chart'),
    path('chartJSON', views.LineChartJSONView.as_view(), name='line_chart_json'),
]