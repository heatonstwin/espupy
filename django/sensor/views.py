import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseNotFound
from django.http import JsonResponse
from django.views.generic import CreateView

# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView

from utilities.views import ListViewChartMixin
from .models import Sensor, Device, SensorReading


class SensorCreateView(CreateView):

    queryset = Sensor.objects.all()

    def post(self, request, *args, **kwargs):
        payload = request.POST.copy().dict()
        payload.pop('csrfmiddlewaretoken', None)

        try:
            device = Device.objects.get(model=payload.pop('device'))
        except ObjectDoesNotExist:
            return HttpResponseNotFound('<h1>Device "{}" Fot Found</h1>'.format(payload['device']))
        else:
            payload['device'] = device

        sensor, created = Sensor.objects.update_or_create(mac=payload['mac'], defaults=payload)
        respose = JsonResponse({'sensor': model_to_dict(sensor)})
        return respose


class SensorReadingCreateView(CreateView):

    queryset = SensorReading.objects.all()

    def post(self, request, *args, **kwargs):
        payload = request.POST.copy().dict()
        payload.pop('csrfmiddlewaretoken', None)

        sensor = Sensor.objects.get(id=payload.pop('sensor'))
        reading = SensorReading.objects.create(sensor=sensor, **payload)

        next_reading = reading.timestamp + datetime.timedelta(seconds=sensor.poll_rate)
        sensor.next_reading=next_reading
        sensor.save()

        respose = JsonResponse({
            'reading': model_to_dict(reading),
            'sleep': (next_reading - reading.timestamp).total_seconds()
        })
        return respose


class SensorReadingListView(ListView):

    model = SensorReading
    paginate_by = 200

    def get_queryset(self):
        sensor_id = self.kwargs.get('pk')
        readings = self.model.objects.filter(sensor_id=sensor_id)
        return readings


class SensorDetailView(DetailView):

    model = Sensor

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({'sensor': model_to_dict(context['object'])})


class SensorListView(ListView):

    model = Sensor


class SensorReadingListChartView(ListViewChartMixin):

    model = SensorReading
    trace_type = 'Scatter'
    trace_name_field = 'sensor__location'
    trace_x_field = 'timestamp'
    trace_y_field = 'measurement'
    trace_options = {
        'line': dict(width=1),
        'mode': 'lines'
    }
    layout_title = 'DHT11 Measurements'
    layout_x_axis_title = 'Timestamp'
    layout_y_axis_title = 'Measurement (F)'

    def get_queryset(self):
        queryset = super(SensorReadingListChartView, self).get_queryset()
        sensor_model = self.kwargs.get('model')
        location = self.kwargs.get('location')
        if location:
            queryset = queryset.filter(
                sensor__device__model=sensor_model,
                sensor__location=location)
        return queryset
