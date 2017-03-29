from django.contrib import admin

# Register your models here.

from .models import (
    Sensor,
    SensorReading,
    Device
)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    pass


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):

    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    list_display = ('sensor', 'measurement', 'unit', 'timestamp')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    pass

