import time

from machine import Pin
from machine import PWM
from machine import UART
from machine import Timer

uart=UART(2,9600,rx=18,tx=19)

DIR0 = Pin(26,Pin.OUT) #方向-
DIR1 = Pin(25,Pin.OUT) #方向+

PUL0 = Pin(14,Pin.OUT) #脉冲-
#PUL1 = Pin(27,Pin.OUT) #脉冲+

DIR0.value(0) #方向-接地
PUL0.value(0) #脉冲-接地

motion = 0 #0:停止, 1:正转, 2:反转

timer0 = Timer(0)

def ting():
    PUL1 = PWM(Pin(27), freq=1, duty=0)

def zhengzhuan():
    DIR1.value(1)
    PUL1 = PWM(Pin(27), freq=400, duty=512)

def fanzhuan():
    DIR1.value(0)
    PUL1 = PWM(Pin(27), freq=400, duty=512)

def timer_callback(timer):
    global motion
    if motion == 1:
        zhengzhuan()
    elif motion == 2:
        fanzhuan()
    elif motion == 0:
        ting()

timer0.init(period=20, mode=Timer.PERIODIC, callback=timer_callback)

while True:
    if uart.any():
        text=uart.readline()
        if text == b'1\r\n':
            motion = 1
        elif text == b'2\r\n':
            motion = 2
        elif text == b'0\r\n':
            motion = 0