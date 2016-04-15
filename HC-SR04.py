# HC-SR04.py - driver for ultrasonic distance meter
#    Test distance = (time * High speed of sound (340M / S))

import pyb, micropython
from pyb import Pin, Timer, ExtInt
micropython.alloc_emergency_exception_buf(100)

pyb.enable_irq()

class UltraSonicMeter(object):

    def __init__(self):
        self.tmp = self.time = 0
        self.cnt = 0
        self.fr = 0
        self.trig = Pin('X12', Pin.OUT_PP, Pin.PULL_NONE)
        echoR = Pin('X1', Pin.IN, Pin.PULL_NONE)
        echoF = Pin('X2', Pin.IN, Pin.PULL_NONE)
        self.micros = pyb.Timer(5, prescaler=83, period=0x3fffffff)
        self.timer = Timer(2, freq=1000)
        self.timer.period(3600)
        self.timer.prescaler(1375)
        self.timer.callback(lambda e: self.run_trig())
        extR = ExtInt(echoR, ExtInt.IRQ_RISING, Pin.PULL_NONE, self.start_count)
        extF = ExtInt(echoF, ExtInt.IRQ_FALLING, Pin.PULL_NONE, self.read_dist)

    def run_trig(self):
        self.trig.high()
        pyb.udelay(1)
        self.trig.low()

    def start_count(self, line):
        self.micros.counter(0)
        self.time = self.micros.counter()
        self.timer.counter(0)

    def read_dist(self, line):
        end = self.micros.counter()
        micros = end-self.time
        distP1 = micros//5
        distP2 = micros//6
        distP3 = (distP1-distP2)//10*2
        dist = distP2+distP3

        if dist != 0:
            self.cnt += 1
            self.fr += dist

        if self.cnt == 15:
            tmp = self.tmp
            dist = self.fr//self.cnt
            if tmp != dist:
                print(dist, 'mm')
                self.tmp = dist
            self.cnt = 0
            self.fr  = 0

meter = UltraSonicMeter()
