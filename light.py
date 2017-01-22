import time
from machine import ADC


class Light:
    def __init__(self, threshold=900):
        self.sensor = ADC(0)
        self.on = False
        self.switch_on = True
        self.threshold = threshold

    def run(self):
        while True:
            self.sense(self.sensor.read())
            time.sleep(0.1)

    def sense(self, reading):
        print('reading={}'.format(reading))
        if not self.switch_on:
            self.on = False
            print('Switch has turned the light off')
            return

        if reading <= self.threshold and not self.on:
            print('Turning the light on')
            self.on = True

