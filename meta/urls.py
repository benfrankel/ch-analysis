from meta import views

from django.conf.urls import url


app_name = 'meta'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^battles', views.battles, name='battles'),
]
