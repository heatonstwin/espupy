import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponseNotFound
from django.http import JsonResponse
from django.views.generic import CreateView

# Create your views here.
from django.views.generic import DetailView

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


class SensorDetailView(DetailView):

    model = Sensor

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({'sensor': model_to_dict(context['object'])})

