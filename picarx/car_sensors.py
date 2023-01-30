import time
from enum import Enum
try:
    from robot_hat import ADC
    from robot_hat import Grayscale_Module, Ultrasonic
    from robot_hat.utils import reset_mcu
    reset_mcu()
    time.sleep (0.01)
except ImportError:
    print ("This computer does not appear to be a PiCar -X system (robot_hat is not present). Shadowing hardware calls with substitute functions ")
    from sim_robot_hat import *
import os
import atexit
import math 


class PicarxSensor(object):
    def __init__(self, greyscale_pins:list = ['A0', 'A1', 'A2'], reference = 1500):
        #Greyscale Dataa
        self.chn_0 = ADC(greyscale_pins[0])
        self.chn_1 = ADC(greyscale_pins[1])
        self.chn_2 = ADC(greyscale_pins[2])
    
    def read_greyscale_data(self):
        output = []
        output.append(self.chn_0.read())
        output.append(self.chn_1.read())
        output.append(self.chn_2.read())
        return output


class Interpreter(object):
    #Sensitivity, true = darker, false = lighter
    def __init__(self, sensitivity=500, polarity=True, initial_greyscale=[1500,1500,1500]):
        self.sensitivity = sensitivity
        self.polarity = polarity
        self.old_greyscale_data = initial_greyscale
    
    def react(self, new_greyscale_data):
        #Check for drop on sides
        drop_left = new_greyscale_data[0]-self.old_greyscale_data[0]
        drop_right = new_greyscale_data[2]-self.old_greyscale_data[2]
        if abs(drop_left) > self.sensitivity or abs(drop_right) > self.sensitivity:
            print("drop detected")
        if self.polarity:
            if drop_left <= -self.sensitivity or drop_right <= -self.sensitivity:
                if drop_left <= -self.sensitivity:
                    pass
                else:
                    pass
        else:
            if drop_left >= self.sensitivity or drop_right >= self.sensitivity:
                if drop_left >= self.sensitivity:
                    pass
                else:
                    pass

            



if __name__=='__main__':
    sensors = PicarxSensor()
    interpreter = Interpreter() 
    while True:
        interpreter.react(sensors.read_greyscale_data())
        
