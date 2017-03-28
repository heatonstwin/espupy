from django.db import models

# Create your models here.


class Device(models.Model):

    TEMP_HUMID = 'TH'
    LIGHT = 'LI'

    FUNCTION_CHOICES = (
        (TEMP_HUMID, 'Temperature and Humidity'),
        (LIGHT, 'Light'),
    )

    function = models.CharField(max_length=64, choices=FUNCTION_CHOICES)
    model = models.CharField(max_length=64)

    def __str__(self):
        return '{function}: {model}'.format(
            model=self.model,
            function=self.get_function_display()
        )

    class Meta:
        ordering = ['model']


class Sensor(models.Model):

    mac = models.CharField(max_length=17)
    address = models.GenericIPAddressField(protocol='IPv4')
    netmask = models.GenericIPAddressField(protocol='IPv4')
    gateway = models.GenericIPAddressField(protocol='IPv4')
    device = models.ForeignKey(Device)
    location = models.CharField(max_length=128)
    poll_rate = models.IntegerField(default=60)

    def __str__(self):
        return '{location} - {device} ({address})'.format(
            location=self.location,
            device=self.device.model,
            address=self.address
        )

    class Meta:
        ordering = ['address']


class SensorReading(models.Model):

    FAHRENHEIT = 'F'
    CELSIUS = 'C'
    INT = 'INT'
    FLT = 'FLT'

    UNIT_CHOICES = (
        (FAHRENHEIT, 'F'),
        (CELSIUS, 'C'),
        (INT, 'Integer'),
        (FLT, 'Float'),
    )

    sensor = models.ForeignKey(Sensor)
    unit = models.CharField(max_length=16, choices=UNIT_CHOICES)
    measurement = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{sensor}: {measurement} {unit}'.format(
            sensor=self.sensor.address,
            measurement=self.measurement,
            unit=self.get_unit_display()
        )

    class Meta:
        ordering = ['-timestamp']

