from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.OfficialListView.as_view(), name='index'),
    url(r'^officials/(?P<pk>\d+)-(?P<slug>[a-z0-9\-]+)/$',
        views.OfficialDetailView.as_view(), name='official-detail'),
    url(r'^officials/(?P<pk>\d+)-(?P<slug>[a-z0-9\-]+)/add-meeting/$',
        views.MeetingCreateView.as_view(), name='add-meeting'),
    url(r'^call-us-rep/', views.CallUsRepView.as_view(), name='call-us-rep'),
]
