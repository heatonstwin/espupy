"""iot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from .views import SensorCreateView, SensorReadingCreateView,\
    SensorDetailView, SensorListView, SensorReadingListChartView


urlpatterns = [
    url(r'^register$', SensorCreateView.as_view(), name='sensor-create'),
    url(r'^sense$', SensorReadingCreateView.as_view(), name='sensor-sense'),
    url(r'^(?P<pk>\d+)$', SensorDetailView.as_view(), name='sensor-detail'),
    url(r'^(?P<model>\w+)/readings/chart$', SensorReadingListChartView.as_view(), name='sensor-reading-list-chart'),
    url(r'^(?P<model>\w+)/readings/location/(?P<location>[\w\W]+)/chart$', SensorReadingListChartView.as_view(), name='sensor-reading-list-chart'),
    url(r'^readings/(?P<pk>\d+)$', SensorListView.as_view(), name='sensor-reading-list'),
    url(r'^list$', SensorListView.as_view(), name='sensor-list')
]
