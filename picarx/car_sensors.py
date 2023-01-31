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
import picarx_improved as px


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
        position = 0
        
        drop_left = self.old_greyscale_data[0]-new_greyscale_data[0]
        drop_middle = self.old_greyscale_data[1]-new_greyscale_data[1]
        drop_right = self.old_greyscale_data[2]-new_greyscale_data[2]
        if (drop_left >= self.sensitivity and self.polarity) or (drop_right >= self.sensitivity and self.polarity) or (drop_middle >= self.sensitivity and self.polarity):
            print(drop_left)
            print(drop_middle)
            print(drop_right)
            summed_drops = abs(drop_middle) + abs(drop_left)+ abs(drop_right)
            if summed_drops != 0:
                drops = [abs(drop_left)/summed_drops, abs(drop_middle)/summed_drops, abs(drop_right)/summed_drops]
                #print(drops)
                position = drops[0]*1 + drops[1]*0 + -1*drops[2]
        #elif drop_left <= self.sensitivity or drop_right <= self.sensitivity or drop_middle <= self.sensitivity and not self.polarity:
        #    summed_drops = abs(drop_middle) + abs(drop_left)+ abs(drop_right)
        ##    if summed_drops != 0:
        #        drops = [abs(drop_left)/summed_drops, abs(drop_middle)/summed_drops, abs(drop_right)/summed_drops]
        #        print(drops)
        #        position = drops[0]*1 + drops[1]*0 + -1*drops[2]
        
        self.old_greyscale_data = new_greyscale_data
        print(new_greyscale_data)
        print("position")
        print(position)
        return position

class Controller(object):
    def __init__(self, scaling=0, angle=35):
        self.scaling = scaling
        self.angle = angle
    
    def steer(self, scaling, px):
        directed_angle = self.scaling*self.angle
        px.set_dir_servo_angle(directed_angle)
        return directed_angle


def steerOnLine():
    car = px.Picarx()
    sensors = PicarxSensor()
    interpreter = Interpreter(initial_greyscale=sensors.read_greyscale_data()) 
    controller = Controller()
    while True:
        controller.steer(interpreter.react(sensors.read_greyscale_data()), car)
        time.sleep(0.5)

if __name__=='__main__':
    steerOnLine()
        
