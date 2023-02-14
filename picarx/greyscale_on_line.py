import time
from enum import Enum
from concurrency import Bus
import concurrent.futures

try:
    from robot_hat import ADC
    from robot_hat import Grayscale_Module, Ultrasonic
    from robot_hat.utils import reset_mcu
    reset_mcu()
    time.sleep (0.01)
except ImportError:
    print ("This computer does not appear to be a PiCar -X system (robot_hat is not present). Shadowing hardware calls with substitute functions ")
    from sim_robot_hat import *

from picarx_improved import Picarx
import logging
from concurrency import Bus

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

    def producer(self, bus:Bus, delay):
        while True:
            bus.write(self.read_greyscale_data())
            time.sleep(delay)




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

    def producer_consumer(self, sensor_bus:Bus, interpreter_bus:Bus, delay):
        while True:
            sensor_data = sensor_bus.read()
            position = self.outputPosition(sensor_data)
            interpreter_bus.write(position)
            print(position)
            time.sleep(delay)

    


class Controller(object):
    def __init__(self, scaling=0, angle=35):
        self.scaling = scaling
        self.angle = angle
        #Setup car
        #self.car = px.Picarx()
        self.car.set_dir_servo_angle(0)
    
    def steer(self, scaling):
        self.scaling = scaling
        #Scale turn angle by position
        directed_angle = self.scaling*self.angle
        return directed_angle

    def moveForward(self): 
        self.car.forward(25)
    
    def consumer(self, bus:Bus, delay):
        while True:
            interpret_data = bus.read()
            #self.steer(interpret_data)
            time.sleep(delay)



def steerOnLine(polarity):
    car = Picarx()
    sensors = PicarxSensor()
    interpreter = Interpreter(polarity=polarity,initial_greyscale=sensors.read_greyscale_data()) 
    controller = Controller()
    sensor_values_bus = Bus(sensors.read_greyscale_data())
    interpreter_bus = Bus(0) 
    sensor_delay = 0.01
    interpreter_delay = 0.01
    controller_delay = 0.01



    with concurrent.futures.ThreadPoolExecutor(max_workers =4) as executor:
            eSensor = executor.submit(sensors.producer,sensor_values_bus, sensor_delay)
            eInterpreter = executor.submit(interpreter.producer_consumer,sensor_values_bus,interpreter_bus,interpreter_delay)
            eController = executor.submit(car.steer, interpreter_bus)
    print("Am I crazy")
    eSensor.result()


        

#Script
if __name__=='__main__':
    try:
        logging.debug("Starting greyscale line following script")
        choice = input("Type 1 for dark case, 0 for light case: ")


        steerOnLine(choice)
    except KeyboardInterrupt:
        logging.debug("Forced to end")
        
