from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^call-us-rep/', views.CallUsRepView.as_view(), name='call-us-rep'),
]
