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
import logging

class PicarxSensor(object):
    def __init__(self, greyscale_pins:list = ['A0', 'A1', 'A2'], reference = 1500):
        #Greyscale Data from ADC pins
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
    def __init__(self, sensitivity=200, polarity=True, initial_greyscale=[1500,1500,1500]):
        self.sensitivity = sensitivity
        self.polarity = polarity
        self.greyscale_data = initial_greyscale
    
    def outputPosition(self, new_greyscale_data):
        #Store new data
        self.greyscale_data = new_greyscale_data
        #Compare data between the readings
        left_middle_difference = self.greyscale_data[1] - self.greyscale_data[0]  
        right_middle_difference = self.greyscale_data[1] - self.greyscale_data[2]
        difference = abs(left_middle_difference - right_middle_difference)
        total_change = abs(left_middle_difference)+abs(right_middle_difference)
        #Check if there is an edge
        if (difference >= self.sensitivity):
            #Dark Edge Case
            if self.polarity and max(left_middle_difference,right_middle_difference) > 0:
                #Decide position by weighted sum
                return -1*(abs(left_middle_difference)/total_change) + 1*(abs(right_middle_difference)/total_change)
            #Light Edge Case
            elif not self.polarity and min(left_middle_difference,right_middle_difference)<0:
                #Decide position by weighted sum
                return -1*(abs(left_middle_difference)/total_change) + 1*(abs(right_middle_difference)/total_change)
        else:
            logging.debug("No edge detected")
        return 0


class Controller(object):
    def __init__(self, scaling=0, angle=35):
        self.scaling = scaling
        self.angle = angle
        #Setup car
        self.car = px.Picarx()
        self.car.set_dir_servo_angle(0)
    
    def steer(self, scaling):
        self.scaling = scaling
        #Scale turn angle by position
        directed_angle = self.scaling*self.angle
        self.car.set_dir_servo_angle(directed_angle)
        return directed_angle

    def moveForward(self): 
        self.car.forward(25)

def steerOnLine(polarity):
    sensors = PicarxSensor()
    interpreter = Interpreter(polarity=polarity,initial_greyscale=sensors.read_greyscale_data()) 
    controller = Controller()
    controller.car.set_dir_servo_angle(0)
    controller.moveForward()
    while True:
        controller.steer(interpreter.outputPosition(sensors.read_greyscale_data()))
        

#Script
if __name__=='__main__':
    try:
        logging.debug("Starting greyscale line following script")
        choice = input("Type 1 for dark case, 0 for light case: ")


        steerOnLine(choice)
    except KeyboardInterrupt:
        logging.debug("Forced to end")
        