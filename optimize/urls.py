from django.conf.urls import url

from optimize import views


app_name = 'optimize'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
