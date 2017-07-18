from django.conf.urls import url

from battles import views


app_name = 'battles'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
