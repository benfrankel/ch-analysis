from optimize import views

from django.conf.urls import url


app_name = 'optimize'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
